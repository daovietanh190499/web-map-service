# wms_app/serializers.py

from rest_framework import serializers
from .models import Image, BaseMap, ArcGISConfig

from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import PredictArea, PredictAreaComponent

import json

class ImageUploadSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    format = serializers.CharField(max_length=255, required=False)
    source = serializers.CharField(max_length=255, required=False)
    satellite_id = serializers.CharField(max_length=255, required=False)
    datetime = serializers.DateTimeField(required=False)
    file = serializers.FileField()

class BaseMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseMap
        fields = '__all__'

class ArcGISConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArcGISConfig
        fields = '__all__'

class PredictAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PredictArea
        fields = ('id', 'created_at', 'updated_at', 'image', 'name')  # Các trường bạn muốn hiển thị

class PredictAreaComponentSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = PredictAreaComponent
        fields = ('id', 'created_at', 'updated_at', 'area', 'options', 'object', 'geom')  # Các trường bạn muốn hiển thị
        geo_field = 'geom'
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        str_opt = data.get("properties", "").get("options", "")
        obj_opt = json.loads(str_opt)
        data["properties"]["options"] = obj_opt
        return data

class DetailPredictAreaSerializer(serializers.ModelSerializer):
    components = PredictAreaComponentSerializer(many=True)
    class Meta:
        model = PredictArea
        fields = ('id', 'created_at', 'updated_at', 'image', 'components')  # Các trường bạn muốn hiển thị

class ImageSerializer(GeoFeatureModelSerializer):
    predictions = PredictAreaSerializer(many=True, read_only=True)
    class Meta:
        model = Image
        geo_field = 'geom'
        # bbox_geo_field = 'bbox_geom'
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data.get("properties", {}).get("resolution"):
            data["properties"]["resolution"] = data.get("properties", {}).get("resolution")*111000
        return data

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