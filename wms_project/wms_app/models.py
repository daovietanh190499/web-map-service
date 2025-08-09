# wms_app/models.py

# from django.db import models
from django.contrib.gis.db import models
from datetime import datetime
import uuid
    
class Image(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    datetime = models.DateTimeField(null=True)
    resolution = models.FloatField(null=True)
    bands = models.IntegerField(null=True)
    filename = models.CharField(max_length=255, null=True)
    filepath = models.CharField(max_length=1000, null=True)
    area = models.FloatField(null=True)
    name = models.CharField(max_length=255, null=True)
    topic = models.CharField(max_length=255, null=True)
    source = models.CharField(max_length=255, null=True)
    satellite_id = models.CharField(max_length=255, null=True)
    format = models.CharField(max_length=255, null=True)
    geom = models.GeometryField(srid=4326, null=True)

class PredictArea(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    image = models.ForeignKey(to=Image, on_delete=models.SET_NULL, related_name="predictions", null=True)

class PredictAreaComponent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    area = models.ForeignKey(to=PredictArea, on_delete=models.CASCADE, related_name="components", null=True)
    object = models.CharField(max_length=100, null=True)
    options = models.CharField(max_length=10000, null=True)
    geom = models.GeometryField(srid=4326, null=True)

class BaseMap(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    service_type = models.CharField(max_length=100, unique=True)  # Uppercase, non-space string
    url = models.URLField(max_length=1000)
    attribution = models.CharField(max_length=500)
    subdomains = models.JSONField(null=True, blank=True)  # Optional string array
    
    class Meta:
        ordering = ['created_at']

class ArcGISConfig(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    portal_url = models.URLField(max_length=1000)
    api_url = models.URLField(max_length=1000)
    
    class Meta:
        verbose_name = "ArcGIS Configuration"
        verbose_name_plural = "ArcGIS Configurations"
