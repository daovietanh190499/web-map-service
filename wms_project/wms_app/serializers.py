# wms_app/serializers.py

from rest_framework import serializers
from .models import Image

from rest_framework_gis.serializers import GeoFeatureModelSerializer

class ImageSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Image
        geo_field = 'geom'
        # bbox_geo_field = 'bbox_geom'
        fields = '__all__'

class SearchGeometrySerializer(serializers.Serializer):
    type = serializers.CharField()
    coordinates = serializers.JSONField()

class ImageFilterSerializer(serializers.Serializer):
    geometry = serializers.JSONField(required=False)
    operation = serializers.CharField(required=False, default='intersects')
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(required=False)
    resolution_min = serializers.FloatField(required=False)
    resolution_max = serializers.FloatField(required=False)
    topic = serializers.CharField(required=False)
    source = serializers.CharField(required=False)
    satellite_id = serializers.CharField(required=False)