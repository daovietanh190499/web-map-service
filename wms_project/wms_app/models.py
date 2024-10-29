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
    geom = models.GeometryField(srid=4326, null=True)
