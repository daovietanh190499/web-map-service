# wms_app/models.py

from django.db import models
from django.contrib.gis.db import models as gis_models

class Image(models.Model):
    datetime = models.DateTimeField()
    area = models.FloatField()
    geolocation = gis_models.PointField()
    name = models.CharField(max_length=255)
    topic = models.CharField(max_length=255)
    source = models.CharField(max_length=255)
    satellite_id = models.CharField(max_length=255)
    image_url = models.URLField()

class Mask(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='masks')
    mask_data = models.JSONField()