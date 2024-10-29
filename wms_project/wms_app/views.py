# views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.db.models.functions import Intersection
from .models import Image
from django.db.models import Q
from .serializers import ImageSerializer, SearchGeometrySerializer, ImageFilterSerializer
from osgeo import gdal, osr
import json
import os
import numpy as np
import rasterio
from rest_framework_gis.filters import InBBoxFilter
from django.shortcuts import render
from PIL import Image as PIL_Image
import io
from django.http import HttpResponse
from wms_app.generate_tiles import Tiles

def index(request):
    return render(request, 'index.html')

# from django.views.generic import ListView
# from vectortiles.views import MVTView

# class MaskView(MVTView, ListView):
#     model = Mask
#     vector_tile_layer_name = "mask"
#     vector_tile_fields = ('name',)
#     vector_tile_geom_name = "geom"

class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

    bbox_filter_field = 'geom'
    filter_backends = (InBBoxFilter,)
    bbox_filter_include_overlapping = True

    img = rasterio.open("/home/coder/3D_Reconstruction/web-map-service/wms_project/data/Hanoi_20240810_S2.jp2")

    @action(detail=False, url_path='jp2/tiles/(?P<z>[0-9]+)/(?P<x>[0-9]+)/(?P<y>[0-9]+).png', methods=['GET'])
    def generate_tile(self, request, z, x, y):
        buffer = io.BytesIO()

        if os.path.exists(f'tiles/image1/{str(z)}/{str(x)}/{str(y)}.png'):
            img = PIL_Image.open(f'tiles/image1/{str(z)}/{str(x)}/{str(y)}.png')
        else:
            tiled = Tiles(image=self.img, zooms=[int(z)], x=int(x), y=int(y), pixels=256, resampling="bilinear")
            img = PIL_Image.fromarray(np.transpose(tiled.tiles.data, (1, 2, 0)))
            if not os.path.exists(f'tiles/image1/{str(z)}/{str(x)}'):
                os.makedirs(f'tiles/image1/{str(z)}/{str(x)}')
            img.save(f'tiles/image1/{str(z)}/{str(x)}/{str(y)}.png')
        
        img.save(buffer, format="PNG")
        buffer.seek(0)

        return HttpResponse(buffer, content_type="image/png")

    @action(detail=False, methods=['post'])
    def scan_folder(self, request):
        """Scan a folder for JP2 files and store their metadata"""
        folder_path = '/home/coder/3D_Reconstruction/web-map-service/wms_project/data/'
        if not folder_path:
            return Response(
                {'error': 'folder_path is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            files_processed = self._scan_jp2_folder(folder_path)
            return Response({
                'message': f'Processed {files_processed} JP2 files',
                'files_processed': files_processed
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def find_overlapping(self, request):
        """Find images that overlap with the given geometry"""
        serializer = SearchGeometrySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Convert GeoJSON to GEOS geometry
        geojson = {
            'type': serializer.validated_data['type'],
            'coordinates': serializer.validated_data['coordinates']
        }
        search_geometry = GEOSGeometry(json.dumps(geojson))
        
        overlapping_images = Image.objects.filter(
            geometry__intersects=search_geometry
        ).select_related()

        return Response(
            ImageSerializer(overlapping_images, many=True).data
        )

    def _scan_jp2_folder(self, folder_path):
        """Scan folder and store JP2 metadata"""
        files_processed = 0

        for filename in os.listdir(folder_path):
            if filename.lower().endswith('.jp2'):
                jp2_path = os.path.join(folder_path, filename)
                if self._store_jp2_metadata(jp2_path):
                    files_processed += 1

        return files_processed

    def _store_jp2_metadata(self, jp2_path):
        """Extract and store JP2 metadata"""
        try:
            ds = gdal.Open(jp2_path)
            if ds is None:
                return False

            # Get geotransform and bounds
            gt = ds.GetGeoTransform()
            width = ds.RasterXSize
            height = ds.RasterYSize

            minx = gt[0]
            maxy = gt[3]
            maxx = gt[0] + width * gt[1]
            miny = gt[3] + height * gt[5]

            # Create GeoJSON polygon for bounds
            geometry_json = {
                'type': 'Polygon',
                'coordinates': [[
                    [minx, miny],
                    [maxx, miny],
                    [maxx, maxy],
                    [minx, maxy],
                    [minx, miny]
                ]]
            }

            # Convert to GEOS geometry
            geometry = GEOSGeometry(json.dumps(geometry_json), srid=4326)

            # Create or update metadata
            Image.objects.update_or_create(
                filename=os.path.basename(jp2_path),
                defaults={
                    'filepath': jp2_path,
                    'geom': geometry,
                    'resolution': gt[1],  # Pixel size in map units
                    'bands': ds.RasterCount
                }
            )

            ds = None
            return True

        except Exception as e:
            print(f"Error processing {jp2_path}: {str(e)}")
            return False

    @action(detail=False, methods=['post'])
    def spatial_query(self, request):
        """Advanced spatial query endpoint"""
        search_geometry = GEOSGeometry(json.dumps(request.data.get('geom')))
        spatial_op = request.data.get('operation', 'intersects')
        
        # Map of supported spatial operations
        spatial_ops = {
            'intersects': 'geom__intersects',
            'contains': 'geom__contains',
            'crosses': 'geom__crosses',
            'disjoint': 'geom__disjoint',
            'equals': 'geom__equals',
            'overlaps': 'geom__overlaps',
            'touches': 'geom__touches',
            'within': 'geom__within',
        }
        
        if spatial_op not in spatial_ops:
            return Response(
                {'error': f'Unsupported spatial operation. Supported operations: {", ".join(spatial_ops.keys())}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Build the filter
        filter_kwargs = {spatial_ops[spatial_op]: search_geometry}
        
        # Apply additional filters if provided
        resolution_min = request.data.get('resolution_min')
        resolution_max = request.data.get('resolution_max')
        if resolution_min is not None:
            filter_kwargs['resolution__gte'] = resolution_min
        if resolution_max is not None:
            filter_kwargs['resolution__lte'] = resolution_max

        # Execute query
        results = Image.objects.filter(**filter_kwargs)
        
        return Response(ImageSerializer(results, many=True).data)

    @action(detail=False, methods=['post'])
    def search(self, request):
        """Advanced search endpoint with multiple filters"""
        serializer = ImageFilterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        filters = Q()
        data = serializer.validated_data

        # Spatial filter
        if 'geometry' in data:
            search_geometry = GEOSGeometry(json.dumps(data['geometry']))
            spatial_op = data.get('operation', 'intersects')
            
            spatial_ops = {
                'intersects': 'geom__intersects',
                'contains': 'geom__contains',
                'crosses': 'geom__crosses',
                'disjoint': 'geom__disjoint',
                'equals': 'geom__equals',
                'overlaps': 'geom__overlaps',
                'touches': 'geom__touches',
                'within': 'geom__within',
            }
            
            if spatial_op not in spatial_ops:
                return Response(
                    {'error': f'Unsupported spatial operation. Supported operations: {", ".join(spatial_ops.keys())}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            filters &= Q(**{spatial_ops[spatial_op]: search_geometry})

        # Temporal filter
        if 'start_date' in data:
            filters &= Q(datetime__gte=data['start_date'])
        if 'end_date' in data:
            filters &= Q(datetime__lte=data['end_date'])

        # Resolution filter
        if 'resolution_min' in data:
            filters &= Q(resolution__gte=data['resolution_min'])
        if 'resolution_max' in data:
            filters &= Q(resolution__lte=data['resolution_max'])

        # Metadata filters
        for field in ['topic', 'source', 'satellite_id']:
            if field in data:
                filters &= Q(**{field: data[field]})

        # Execute query
        results = Image.objects.filter(filters)
        
        return Response(ImageSerializer(results, many=True).data)