# wms_app/serializers.py

from rest_framework import serializers
from .models import Image, BaseMap, ArcGISConfig, Topic, TopicAttachment

from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import PredictArea, PredictAreaComponent

import json

class ImageUploadSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    format = serializers.CharField(max_length=255, required=False)
    source = serializers.CharField(max_length=255, required=False)
    satellite_id = serializers.CharField(max_length=255, required=False)
    datetime = serializers.DateTimeField(required=False)
    bands_order = serializers.CharField(max_length=50, required=False, default='3_2_1')
    file = serializers.FileField()

class ImageUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False)
    format = serializers.CharField(max_length=255, required=False)
    source = serializers.CharField(max_length=255, required=False)
    satellite_id = serializers.CharField(max_length=255, required=False)
    datetime = serializers.DateTimeField(required=False)
    bands_order = serializers.CharField(max_length=50, required=False)
    topic = serializers.CharField(max_length=255, required=False)

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

class TopicAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopicAttachment
        fields = ['id', 'file', 'filename', 'file_size', 'file_type', 'uploaded_at']

class TopicSerializer(serializers.ModelSerializer):
    attachments = TopicAttachmentSerializer(many=True, read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Topic
        fields = ['id', 'topic_name', 'created_date', 'type', 'content', 'area', 'subject', 'created_by', 'created_by_username', 'updated_at', 'attachments']
        read_only_fields = ['id', 'created_date', 'updated_at', 'created_by']

class TopicCreateUpdateSerializer(serializers.ModelSerializer):
    attachments = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        write_only=True
    )
    
    class Meta:
        model = Topic
        fields = ['topic_name', 'type', 'content', 'area', 'subject', 'attachments']
    
    def create(self, validated_data):
        attachments_data = validated_data.pop('attachments', [])
        validated_data['created_by'] = self.context['request'].user
        topic = Topic.objects.create(**validated_data)
        
        for attachment_file in attachments_data:
            TopicAttachment.objects.create(topic=topic, file=attachment_file)
        
        return topic
    
    def update(self, instance, validated_data):
        attachments_data = validated_data.pop('attachments', [])
        
        # Update topic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Handle new attachments if provided
        if attachments_data:
            for attachment_file in attachments_data:
                TopicAttachment.objects.create(topic=instance, file=attachment_file)
        
        return instance

class TopicSearchSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    created_date_from = serializers.DateTimeField(required=False)
    created_date_to = serializers.DateTimeField(required=False)
    type = serializers.CharField(required=False)
    subject = serializers.CharField(required=False)
    area = serializers.CharField(required=False)
    content = serializers.CharField(required=False)