# wms_app/models.py

# from django.db import models
from django.contrib.gis.db import models
from datetime import datetime

class BaseModel(models.Model):
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(auto_now=True, null=True)

class Image(BaseModel):
    datetime = models.DateTimeField(null=True)
    resolution = models.FloatField()
    bands = models.IntegerField()
    filename = models.CharField(max_length=255)
    filepath = models.CharField(max_length=1000)
    area = models.FloatField(null=True)
    name = models.CharField(max_length=255, null=True)
    topic = models.CharField(max_length=255, null=True)
    source = models.CharField(max_length=255, null=True)
    satellite_id = models.CharField(max_length=255, null=True)
    geom = models.GeometryField(srid=4326, null=True)
