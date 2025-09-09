# views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.gis.geos import GEOSGeometry, GeometryCollection
from django.contrib.gis.db.models.functions import Intersection
from .models import Image, PredictArea, BaseMap, ArcGISConfig, Topic, TopicAttachment
from django.db.models import Q
from .serializers import (
    ImageSerializer, SearchGeometrySerializer, ImageFilterSerializer, 
    PredictAreaSerializer, PredictAreaComponentSerializer, ImageUploadSerializer, 
    ImageUpdateSerializer, DetailPredictAreaSerializer, BaseMapSerializer, ArcGISConfigSerializer,
    TopicSerializer, TopicCreateUpdateSerializer, TopicSearchSerializer, TopicAttachmentSerializer
)
from osgeo import gdal, osr
import json
import os
import numpy as np
import rasterio
from datetime import datetime
from rest_framework_gis.filters import InBBoxFilter
from django.shortcuts import render
from PIL import Image as PIL_Image
from PIL import ImageOps
import io
from django.http import HttpResponse, FileResponse
from wms_app.generate_tiles import Tiles
from django.conf import settings
from binascii import a2b_base64
import glob
import subprocess
import shutil
import logging

# Thiết lập logger cho module này
logger = logging.getLogger('wms_app')

def index(request):
    return render(request, 'index.html')

def draw_map(request):
    return render(request, 'draw.html')

def compare_map(request):
    return render(request, 'compare.html')

def test_map(request):
    return render(request, 'new-test.html')

def arcgis_map(request):
    return render(request, 'arcgis.html')

def arcgis_auth(request):
    return render(request, 'arcgis-authen.html')

def topic_management(request):
    return render(request, 'topic.html')

class BaseMapViewSet(viewsets.ModelViewSet):
    queryset = BaseMap.objects.all()
    serializer_class = BaseMapSerializer

class ArcGISConfigViewSet(viewsets.ModelViewSet):
    queryset = ArcGISConfig.objects.all()
    serializer_class = ArcGISConfigSerializer

class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

    bbox_filter_field = 'geom'
    filter_backends = (InBBoxFilter,)
    bbox_filter_include_overlapping = True

    def _reorder_bands(self, data, bands_order):
        """Reorder bands based on bands_order string like '3_2_1' or '1_2_3'
        data shape is (channel, width, height)
        """
        try:
            # Parse bands_order string (e.g., '3_2_1' -> [3, 2, 1])
            band_indices = [int(band) - 1 for band in bands_order.split('_')]  # Convert to 0-based indexing
            
            # band_indices.append(-1)
            # Ensure we don't exceed available bands
            num_bands = data.shape[0]  # First dimension is channels
            band_indices = [idx for idx in band_indices if 0 <= idx < num_bands]
            
            # data shape is (channel, width, height)
            # Return reordered data with same shape
            return data[band_indices]
        except (ValueError, IndexError) as e:
            logger.warning(f"Error parsing bands_order '{bands_order}': {e}. Using default order.")
            return data

    @action(detail=True, url_path='jp2/tiles/(?P<z>[0-9]+)/(?P<x>[0-9]+)/(?P<y>[0-9]+).png', methods=['GET'])
    def generate_tile(self, request, pk, z, x, y):
        
        img_db = self.get_object()

        buffer = io.BytesIO()

        if os.path.exists(f'tiles/{img_db.id}/{str(z)}/{str(x)}/{str(y)}.png'):
            img = PIL_Image.open(f'tiles/{img_db.id}/{str(z)}/{str(x)}/{str(y)}.png')
        else:
            img = rasterio.open(img_db.filepath.replace(".jp2", "_enhanced.jp2"))
            
            # print(img.meta, img.statistics(1), img.statistics(2), img.statistics(3))
            tiled = Tiles(image=img, zooms=[int(z)], x=int(x), y=int(y), pixels=256, resampling="bilinear")
            # print("MAX MIN", np.max(tiled.tiles.data), np.min(tiled.tiles.data))
            # print("DATAAAAAA", z, x, y, tiled.tiles.data, tiled.tiles.data.shape)

            # Get bands_order from database, default to '1_2_3'
            bands_order = getattr(img_db, 'bands_order', '1_2_3')
            
            # tiled.tiles.data.shape is (channel, width, height)
            # Reorder bands based on bands_order
            reordered_data = self._reorder_bands(tiled.tiles.data, bands_order)
            
            # Convert to PIL Image with proper channel arrangement
            # reordered_data shape is (channel, width, height)
            num_channels = tiled.tiles.data.shape[0]
            
            if num_channels >= 3:
                # Take first 3 bands for RGB
                rgb_data = reordered_data[:3]  # (3, width, height)
                # Always use the last channel as alpha
                alpha_data = tiled.tiles.data[-1:]  # (1, width, height)
                
                # Transpose to (width, height, channels) and combine RGB + Alpha
                img = PIL_Image.fromarray(np.concatenate(
                    (np.transpose(rgb_data, (1, 2, 0)),  # (width, height, 3)
                    np.transpose(alpha_data, (1, 2, 0))), axis=-1)  # (width, height, 1)
                )
            else:
                # If less than 3 channels, duplicate the available channels
                if num_channels == 1:
                    # Duplicate single channel for grayscale
                    rgb_data = np.repeat(reordered_data, 3, axis=0)  # (3, width, height)
                elif num_channels == 2:
                    # Use first channel for R and G, second for B
                    rgb_data = np.concatenate([
                        reordered_data[0:1],  # R
                        reordered_data[1:2],  # G  
                        reordered_data[1:2]   # B (duplicate G)
                    ], axis=0)  # (3, width, height)
                
                # Use the last channel as alpha
                alpha_data = reordered_data[-1:]  # (1, width, height)
                
                # Transpose to (width, height, channels) and combine RGB + Alpha
                img = PIL_Image.fromarray(np.concatenate(
                    (np.transpose(rgb_data, (1, 2, 0)),  # (width, height, 3)
                    np.transpose(alpha_data, (1, 2, 0))), axis=-1)  # (width, height, 1)
                )

            if not os.path.exists(f'tiles/{img_db.id}'):
                os.makedirs(f'tiles/{img_db.id}', exist_ok=True)

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

    def _store_jp2_metadata(self, jp2_path, name=None, datetime_=None, format=None, source=None, satellite_id=None, bands_order='3_2_1'):
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
                    'bands': ds.RasterCount,
                    'datetime': datetime_,
                    'source': source,
                    'format': format,
                    'satellite_id': satellite_id,
                    'bands_order': bands_order
                }
            )

            ds = None
            return True

        except Exception as e:
            logger.error(f"Error processing {jp2_path}: {str(e)}")
            return False
        
    @action(detail=False, methods=['post'])
    def upload_image(self, request):
        serializer = ImageUploadSerializer(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data['name']
            uploaded_file = serializer.validated_data['file']
            datetime_ = serializer.validated_data['datetime']
            source = serializer.validated_data['source']
            format = serializer.validated_data['format']
            satellite_id = serializer.validated_data['satellite_id']
            bands_order = serializer.validated_data.get('bands_order', '3_2_1')

            milliseconds = int(datetime.now().timestamp() * 1000)

            # Save the uploaded file to a temporary location
            temp_path = os.path.join("/mnt/data", str(milliseconds) + "_" + "_".join(uploaded_file.name.split()))
            with open(temp_path, 'wb') as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)

            band_stats = []

            subprocess.run([
                "gdalinfo",
                "-stats", 
                temp_path
            ])
            
            ds = gdal.Open(temp_path)

            for i in range(1, ds.RasterCount + 1):
                metadata = ds.GetRasterBand(i).GetMetadata()
                mean = float(metadata.get("STATISTICS_MEAN", "nan"))
                stddev = float(metadata.get("STATISTICS_STDDEV", "nan"))
                band_stats.append((mean, stddev))

            z_score = 2.05374891063182

            gdal_command = [
                "gdal_translate",
                "-b", "1",
                "-scale", str(band_stats[0][0] - z_score*band_stats[0][1]), str(band_stats[0][0] + z_score*band_stats[0][1]), "0", "255",
                "-b", "2",
                "-scale", str(band_stats[1][0] - z_score*band_stats[1][1]), str(band_stats[1][0] + z_score*band_stats[1][1]), "0", "255",
                "-b", "3",
                "-scale", str(band_stats[2][0] - z_score*band_stats[2][1]), str(band_stats[2][0] + z_score*band_stats[2][1]), "0", "255",
                "-of", "JP2OpenJPEG",
                "-ot", "Byte",
                temp_path, temp_path.replace(".jp2", "_enhanced.jp2")
            ]
            logger.debug(f"GDAL command: {gdal_command}")

            subprocess.run(gdal_command)

            # subprocess.run(["gdalenhance", "-equalize", "-of", "JP2OpenJPEG", temp_path.replace(".jp2", "_rgb.jp2"), temp_path.replace(".jp2", "_enhanced.jp2")])
            # subprocess.run(["rm", temp_path.replace(".jp2", "_rgb.jp2")])

            # Process the file with GDAL
            if self._store_jp2_metadata(temp_path, name, datetime_, format, source, satellite_id, bands_order):
                return Response({'message': 'File processed successfully.'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'Failed to process the file.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def update_metadata(self, request, pk=None):
        """Update satellite image metadata"""
        try:
            image = self.get_object()
            serializer = ImageUpdateSerializer(data=request.data)
            
            if serializer.is_valid():
                # Update only provided fields
                update_data = serializer.validated_data
                
                # Map frontend field names to model field names
                field_mapping = {
                    'name': 'name',
                    'format': 'format', 
                    'source': 'source',
                    'satellite_id': 'satellite_id',
                    'datetime': 'datetime',
                    'bands_order': 'bands_order',
                    'topic': 'topic'
                }
                
                # Update fields that are provided
                for frontend_field, model_field in field_mapping.items():
                    if frontend_field in update_data:
                        setattr(image, model_field, update_data[frontend_field])
                
                image.save()
                
                return Response({
                    'message': 'Metadata updated successfully',
                    'image': ImageSerializer(image).data
                }, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Image.DoesNotExist:
            return Response(
                {'error': 'Image not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error updating metadata: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def download(self, request, pk=None):
        """Download satellite image file with authentication"""
        try:
            image = self.get_object()
            
            # Check if file exists
            if not image.filepath or not os.path.exists(image.filepath):
                return Response(
                    {'error': 'Image file not found on server'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Determine filename for download
            filename = image.filename or image.name or f"satellite_image_{image.id}"
            if not filename.endswith(('.jp2', '.tif', '.tiff', '.png', '.jpg', '.jpeg')):
                filename += '.jp2'  # Default extension for satellite images
            
            # Open and serve the file
            try:
                file_obj = open(image.filepath, 'rb')
            except Exception as e:
                return Response(
                    {'error': f'Error opening file: {str(e)}'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Determine content type based on file extension
            import mimetypes
            content_type, _ = mimetypes.guess_type(image.filepath)
            if not content_type:
                content_type = 'application/octet-stream'
            
            # Create file response with proper headers
            response = FileResponse(
                file_obj,
                content_type=content_type
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            response['Content-Length'] = os.path.getsize(image.filepath)
            response['Cache-Control'] = 'no-cache'
            
            return response
            
        except Image.DoesNotExist:
            return Response(
                {'error': 'Image not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error downloading image: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated])
    def clear_tiles(self, request, pk=None):
        """Clear all rendered tiles for a satellite image"""
        try:
            image = self.get_object()
            tiles_dir = f'tiles/{image.id}'
            
            # Check if tiles directory exists
            if not os.path.exists(tiles_dir):
                return Response(
                    {'message': 'No tiles found for this image'}, 
                    status=status.HTTP_200_OK
                )
            
            # Count tiles before deletion
            tile_count = 0
            for root, dirs, files in os.walk(tiles_dir):
                tile_count += len([f for f in files if f.endswith('.png')])
            
            # Remove the entire tiles directory
            shutil.rmtree(tiles_dir)
            
            return Response({
                'message': f'Successfully cleared {tile_count} tiles for image {image.id}',
                'tiles_cleared': tile_count
            }, status=status.HTTP_200_OK)
            
        except Image.DoesNotExist:
            return Response(
                {'error': 'Image not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error clearing tiles: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated])
    def delete_image(self, request, pk=None):
        """Delete satellite image file and its database record"""
        try:
            image = self.get_object()
            image_name = image.name or image.filename or f"image_{image.id}"
            
            # Check if file exists and delete it
            if image.filepath and os.path.exists(image.filepath):
                try:
                    os.remove(image.filepath)
                except Exception as e:
                    return Response(
                        {'error': f'Error deleting file: {str(e)}'}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            
            # Delete tiles directory if it exists
            tiles_dir = f'tiles/{image.id}'
            if os.path.exists(tiles_dir):
                try:
                    shutil.rmtree(tiles_dir)
                except Exception as e:
                    # Log error but don't fail the operation
                    logger.warning(f'Could not delete tiles directory: {str(e)}')
            
            # Delete database record
            image.delete()
            
            return Response({
                'message': f'Successfully deleted image "{image_name}" and all associated files',
                'deleted_image_id': pk
            }, status=status.HTTP_200_OK)
            
        except Image.DoesNotExist:
            return Response(
                {'error': 'Image not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error deleting image: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
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

class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter topics based on user permissions"""
        if self.request.user.is_superuser:
            return Topic.objects.all()
        return Topic.objects.filter(created_by=self.request.user)
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TopicCreateUpdateSerializer
        return TopicSerializer
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search topics with filters"""
        serializer = TopicSearchSerializer(data=request.query_params)
        if serializer.is_valid():
            queryset = Topic.objects.all()
            
            # Apply filters
            if serializer.validated_data.get('name'):
                queryset = queryset.filter(
                    topic_name__icontains=serializer.validated_data['name']
                )
            
            if serializer.validated_data.get('created_date_from'):
                queryset = queryset.filter(
                    created_date__gte=serializer.validated_data['created_date_from']
                )
            
            if serializer.validated_data.get('created_date_to'):
                queryset = queryset.filter(
                    created_date__lte=serializer.validated_data['created_date_to']
                )
            
            if serializer.validated_data.get('type'):
                queryset = queryset.filter(type=serializer.validated_data['type'])
            
            if serializer.validated_data.get('subject'):
                queryset = queryset.filter(
                    subject__icontains=serializer.validated_data['subject']
                )
            
            if serializer.validated_data.get('area'):
                queryset = queryset.filter(
                    area__icontains=serializer.validated_data['area']
                )
            
            if serializer.validated_data.get('content'):
                queryset = queryset.filter(
                    content__icontains=serializer.validated_data['content']
                )
            
            # Serialize results with limited fields for search results
            results = []
            for topic in queryset:
                results.append({
                    'id': topic.id,
                    'topic_name': topic.topic_name,
                    'created_date': topic.created_date,
                    'created_by': topic.created_by.username if topic.created_by else None,
                    'type': topic.type,
                    'subject': topic.subject
                })
            
            return Response(results)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def add_attachment(self, request, pk=None):
        """Add attachment to a topic"""
        topic = self.get_object()
        file_obj = request.FILES.get('file')
        
        if not file_obj:
            return Response(
                {'error': 'No file provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        attachment = TopicAttachment.objects.create(
            topic=topic,
            file=file_obj
        )
        
        return Response(TopicAttachmentSerializer(attachment).data)
    
    @action(detail=True, methods=['delete'])
    def remove_attachment(self, request, pk=None):
        """Remove attachment from a topic"""
        topic = self.get_object()
        attachment_id = request.data.get('attachment_id')
        
        try:
            attachment = topic.attachments.get(id=attachment_id)
            attachment.delete()
            return Response({'message': 'Attachment removed successfully'})
        except TopicAttachment.DoesNotExist:
            return Response(
                {'error': 'Attachment not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'], url_path='attachments/(?P<attachment_id>[^/.]+)/debug')
    def debug_attachment(self, request, attachment_id=None):
        """Debug endpoint to check attachment file paths"""
        try:
            attachment = TopicAttachment.objects.get(id=attachment_id)
            
            import os
            from django.conf import settings
            
            debug_info = {
                'attachment_id': str(attachment.id),
                'filename': attachment.filename,
                'file_name': attachment.file.name,
                'file_path': getattr(attachment.file, 'path', 'No path attribute'),
                'media_root': settings.MEDIA_ROOT,
                'media_url': settings.MEDIA_URL,
                'file_size': attachment.file_size,
                'file_type': attachment.file_type,
                'uploaded_at': attachment.uploaded_at,
            }
            
            # Check various possible file paths
            possible_paths = [
                attachment.file.path if hasattr(attachment.file, 'path') else None,
                os.path.join(settings.MEDIA_ROOT, attachment.file.name),
                os.path.join('/mnt/data', attachment.file.name),
                os.path.join('/mnt/data', 'topic_attachments', attachment.filename),
                os.path.join(settings.MEDIA_ROOT, 'topic_attachments', attachment.filename),
            ]
            
            path_checks = {}
            for i, path in enumerate(possible_paths):
                if path:
                    path_checks[f'path_{i}'] = {
                        'path': path,
                        'exists': os.path.exists(path),
                        'is_file': os.path.isfile(path) if os.path.exists(path) else False,
                        'size': os.path.getsize(path) if os.path.exists(path) else None
                    }
            
            debug_info['path_checks'] = path_checks
            
            return Response(debug_info)
            
        except TopicAttachment.DoesNotExist:
            return Response(
                {'error': 'Attachment not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Debug error: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='attachments/(?P<attachment_id>[^/.]+)')
    def download_attachment(self, request, attachment_id=None):
        """Download a specific attachment"""
        try:
            attachment = TopicAttachment.objects.get(id=attachment_id)
            
            # Check if user has permission to access this attachment
            if not request.user.is_superuser and attachment.topic.created_by != request.user:
                return Response(
                    {'error': 'Permission denied'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Check if file exists
            if not attachment.file:
                return Response(
                    {'error': 'File not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Try to open the file - this will handle the actual file path resolution
            try:
                file_obj = attachment.file.open('rb')
            except Exception as e:
                # If the file doesn't exist at the expected path, try alternative paths
                import os
                from django.conf import settings
                
                # Try different possible file paths
                possible_paths = [
                    attachment.file.path,  # Full path from Django
                    os.path.join(settings.MEDIA_ROOT, attachment.file.name),  # MEDIA_ROOT + file name
                    os.path.join('/mnt/data', attachment.file.name),  # Direct path
                    os.path.join('/mnt/data', 'topic_attachments', attachment.filename),  # Alternative structure
                    os.path.join(settings.MEDIA_ROOT, 'topic_attachments', attachment.filename),  # MEDIA_ROOT + topic_attachments + filename
                    os.path.join('/home/wms/topic_attachments', attachment.filename),  # MEDIA_ROOT + topic_attachments + filename
                ]
                
                file_found = False
                for path in possible_paths:
                    if os.path.exists(path):
                        try:
                            file_obj = open(path, 'rb')
                            file_found = True
                            break
                        except Exception:
                            continue
                
                if not file_found:
                    return Response(
                        {'error': f'File not found on disk. Tried paths: {possible_paths}'}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            # Determine content type based on file extension
            import mimetypes
            content_type, _ = mimetypes.guess_type(attachment.filename)
            if not content_type:
                content_type = 'application/octet-stream'
            
            # Create file response with proper headers
            response = FileResponse(
                file_obj,
                content_type=content_type
            )
            response['Content-Disposition'] = f'attachment; filename="{attachment.filename}"'
            response['Content-Length'] = attachment.file_size
            response['Cache-Control'] = 'no-cache'
            
            return response
            
        except TopicAttachment.DoesNotExist:
            return Response(
                {'error': 'Attachment not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error downloading file: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='field-values')
    def get_field_values(self, request):
        """Get all unique values for Type, Subject, and Area fields with statistics"""
        try:
            from django.db.models import Count
            
            # Get unique values with counts for each field
            type_values = Topic.objects.values('type').annotate(count=Count('type')).order_by('-count')
            subject_values = Topic.objects.values('subject').annotate(count=Count('subject')).order_by('-count')
            area_values = Topic.objects.values('area').annotate(count=Count('area')).order_by('-count')
            
            # Format the response
            response_data = {
                'types': [
                    {
                        'value': item['type'],
                        'count': item['count'],
                        'label': self._get_type_label(item['type'])
                    }
                    for item in type_values if item['type']
                ],
                'subjects': [
                    {
                        'value': item['subject'],
                        'count': item['count']
                    }
                    for item in subject_values if item['subject']
                ],
                'areas': [
                    {
                        'value': item['area'],
                        'count': item['count']
                    }
                    for item in area_values if item['area']
                ]
            }
            
            return Response(response_data)
            
        except Exception as e:
            return Response(
                {'error': f'Error getting field values: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_type_label(self, type_value):
        """Get display label for type value"""
        type_labels = {
            'BC_tin': 'BC tin',
            'Thong_tin_DTCB': 'Thông tin ĐTCB',
            'Chua_xac_dinh': 'Chưa xác định'
        }
        return type_labels.get(type_value, type_value)