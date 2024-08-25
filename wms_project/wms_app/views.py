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

class MaskViewSet(viewsets.ModelViewSet):
    queryset = Mask.objects.all()
    serializer_class = MaskSerializer