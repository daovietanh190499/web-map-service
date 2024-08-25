# wms_app/serializers.py

from rest_framework import serializers
from .models import Image, Mask

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'

class MaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mask
        fields = '__all__'