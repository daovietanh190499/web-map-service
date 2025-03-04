# views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.gis.geos import GEOSGeometry, GeometryCollection
from django.contrib.gis.db.models.functions import Intersection
from .models import Image, PredictArea
from django.db.models import Q
from .serializers import ImageSerializer, SearchGeometrySerializer, ImageFilterSerializer, PredictAreaSerializer, PredictAreaComponentSerializer, ImageUploadSerializer, DetailPredictAreaSerializer
from osgeo import gdal, osr
import json
import os
import numpy as np
import rasterio
from datetime import datetime
from rest_framework_gis.filters import InBBoxFilter
from django.shortcuts import render
from PIL import Image as PIL_Image
import io
from django.http import HttpResponse, FileResponse
from wms_app.generate_tiles import Tiles
from django.conf import settings
from binascii import a2b_base64
import glob

def index(request):
    return render(request, 'index.html')

def draw_map(request):
    return render(request, 'draw.html')

def compare_map(request):
    return render(request, 'compare.html')

def test_map(request):
    return render(request, 'test.html')

class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

    bbox_filter_field = 'geom'
    filter_backends = (InBBoxFilter,)
    bbox_filter_include_overlapping = True

    @action(detail=True, url_path='jp2/tiles/(?P<z>[0-9]+)/(?P<x>[0-9]+)/(?P<y>[0-9]+).png', methods=['GET'])
    def generate_tile(self, request, pk, z, x, y):
        
        img_db = self.get_object()

        buffer = io.BytesIO()

        if os.path.exists(f'tiles/{img_db.id}/{str(z)}/{str(x)}/{str(y)}.png'):
            img = PIL_Image.open(f'tiles/{img_db.id}/{str(z)}/{str(x)}/{str(y)}.png')
        else:
            img = rasterio.open(img_db.filepath)
            tiled = Tiles(image=img, zooms=[int(z)], x=int(x), y=int(y), pixels=256, resampling="bilinear")
            img = PIL_Image.fromarray(np.transpose(tiled.tiles.data, (1, 2, 0)))
            if not os.path.exists(f'tiles/{img_db.id}/{str(z)}/{str(x)}'):
                os.makedirs(f'tiles/{img_db.id}/{str(z)}/{str(x)}')
            img.save(f'tiles/{img_db.id}/{str(z)}/{str(x)}/{str(y)}.png')
        
        img.save(buffer, format="PNG")
        buffer.seek(0)

        return HttpResponse(buffer, content_type="image/png")

    @action(detail=False, methods=['post'])
    def scan_folder(self, request):
        """Scan a folder for JP2 files and store their metadata"""
        folder_path = '/mnt/data/'
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

    def _store_jp2_metadata(self, jp2_path, name=None):
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
                    'name': os.path.basename(jp2_path) if name is None else name,
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
    def upload_image(self, request):
        serializer = ImageUploadSerializer(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data['name']
            uploaded_file = serializer.validated_data['file']

            milliseconds = int(datetime.now().timestamp() * 1000)

            # Save the uploaded file to a temporary location
            temp_path = os.path.join("/mnt/data", str(milliseconds) + "_" + "_".join(uploaded_file.name.split()))
            with open(temp_path, 'wb') as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)

            # Process the file with GDAL
            if self._store_jp2_metadata(temp_path, name):
                return Response({'message': 'File processed successfully.'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'Failed to process the file.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
    
class PredictAreaViewSet(viewsets.ModelViewSet):
    queryset = PredictArea.objects.all()
    serializer_class = PredictAreaSerializer

    def retrieve(self, request, pk):
        instance = self.get_object()
        return Response(DetailPredictAreaSerializer(instance).data)

    @action(detail=False, methods=['POST'], url_name='save-area')
    def save_area(self, request):
        features_data = request.data.pop('components', [])
        
        # Create PredictArea first
        data = dict(request.data)
        area_serializer = PredictAreaSerializer(data=data)
        
        if area_serializer.is_valid():
            predict_area = area_serializer.save()
            
            # Create PredictAreaComponent for each geometry
            for feature in features_data:
                geom = feature.get("geom")
                component_data = {
                    'area': predict_area.id,
                    'geom': GEOSGeometry(json.dumps(geom)) if geom else None,
                    'options': json.dumps(feature.get('options', {})),
                    'object': feature.get('object')
                }
                
                component_serializer = PredictAreaComponentSerializer(data=component_data)
                if component_serializer.is_valid():
                    component_serializer.save()
                    image_uri = feature.get('image_uri')
                    if not ( image_uri is None ):
                        base64_str = image_uri.split("base64,")
                        binary_data = a2b_base64(base64_str[1])
                        image_name = component_serializer.instance.id
                        with open(f'/mnt/data/prediction_image_{str(image_name)}{".png" if "png" in base64_str[0] else ".jpg"}', 'wb') as fd:
                            fd.write(binary_data)
                            fd.close()
                else:
                    # If component save fails, delete the predict area and return error
                    predict_area.delete()
                    return Response(component_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(area_serializer.data, status=status.HTTP_201_CREATED)
        return Response(area_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['GET'], url_name='get-image')
    def get_image(self, request, pk):
        list_prediction_image = glob.glob(f'/mnt/data/prediction_image_{str(pk)}.*')
        if len(list_prediction_image) > 0:
            return FileResponse(open(list_prediction_image[0], 'rb'))
        else:
            Response(status=status.HTTP_404_NOT_FOUND)
# from django.db.models import F
# from django.db.models.functions import AsEWKT
# from django.db import connection

# def get_arc_gis(request):
#     with connection.cursor() as cursor:
#         cursor.execute('''
#             SELECT name, ST_AsEWKT(shape) as geom 
#             FROM spatial_table
#         ''')
#         results = cursor.fetchall()