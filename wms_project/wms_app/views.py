# wms_app/views.py

from django.shortcuts import render
from rest_framework import viewsets
from .models import Image, Mask
from .serializers import ImageSerializer, MaskSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings
import uuid
import boto3
from botocore.exceptions import ClientError

# Initialize boto3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    endpoint_url=settings.AWS_S3_ENDPOINT_URL,
    region_name=settings.AWS_S3_REGION_NAME
)

def index(request):
    return render(request, 'index.html')

class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

    @action(detail=False, methods=['POST'])
    def upload_image(self, request):
        file = request.FILES.get('image')
        if not file:
            return Response({'error': 'No image file provided'}, status=400)

        # Generate a unique filename
        file_extension = file.name.split('.')[-1]
        filename = f"{uuid.uuid4()}.{file_extension}"

        try:
            # Upload file to Minio (S3-compatible storage)
            s3_client.upload_fileobj(
                file,
                settings.AWS_STORAGE_BUCKET_NAME,
                filename,
                ExtraArgs={
                    'ContentType': file.content_type,
                    'ACL': settings.AWS_DEFAULT_ACL
                }
            )

            # Create image URL
            image_url = f"{settings.AWS_S3_ENDPOINT_URL}/{settings.AWS_STORAGE_BUCKET_NAME}/{filename}"

            # Create Image object
            serializer = self.get_serializer(data={**request.data, 'image_url': image_url})
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

            return Response(serializer.data, status=201)

        except ClientError as e:
            return Response({'error': str(e)}, status=500)


import os
from django.http import HttpResponse, Http404
from django.conf import settings
from osgeo import gdal
from PIL import Image
import io

# Set the path to your JP2 file
JP2_FILE_PATH = os.path.join(settings.BASE_DIR, 'data/your_image.jp2')

def generate_tile(request, z, x, y):
    try:
        # Open the JP2 file
        dataset = gdal.Open(JP2_FILE_PATH)
        if dataset is None:
            raise Http404("JP2 file not found")

        # Calculate the tile bounds
        tile_size = 256
        zoom = int(z)
        x_tile = int(x)
        y_tile = int(y)

        # Get geographic bounds from the raster
        width = dataset.RasterXSize
        height = dataset.RasterYSize
        geotransform = dataset.GetGeoTransform()

        # Calculate pixel coordinates based on zoom and tile indices
        scale = 2 ** zoom
        x_min = (x_tile * tile_size) / scale
        x_max = ((x_tile + 1) * tile_size) / scale
        y_min = (y_tile * tile_size) / scale
        y_max = ((y_tile + 1) * tile_size) / scale

        # Read raster data in the requested area
        gdal_translate = gdal.Translate(
            '/vsimem/tile.png', dataset,
            projWin=[x_min, y_max, x_max, y_min],
            width=tile_size,
            height=tile_size
        )
        
        # Open and read the translated image
        tile_data = gdal_translate.ReadAsArray()
        if tile_data is None:
            raise Http404("Failed to read tile data")

        # Convert to a PIL Image and then to PNG
        img = Image.fromarray(tile_data)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        # Return image as HTTP response
        return HttpResponse(buffer, content_type="image/png")

    except Exception as e:
        raise Http404(f"Tile generation error: {e}")


class MaskViewSet(viewsets.ModelViewSet):
    queryset = Mask.objects.all()
    serializer_class = MaskSerializer