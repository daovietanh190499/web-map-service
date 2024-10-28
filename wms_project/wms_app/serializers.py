# wms_app/serializers.py

from rest_framework import serializers
from .models import Image

from rest_framework_gis.serializers import GeoFeatureModelSerializer

class ImageSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Image
        geo_field = 'geom'
        bbox_geo_field = 'bbox_geom'
        fields = '__all__'

class SearchGeometrySerializer(serializers.Serializer):
    type = serializers.CharField()
    coordinates = serializers.JSONField()