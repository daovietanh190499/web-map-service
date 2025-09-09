# wms_app/models.py

# from django.db import models
from django.contrib.gis.db import models
from django.contrib.auth.models import User
from datetime import datetime
import uuid
    
class Image(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    datetime = models.DateTimeField(null=True)
    resolution = models.FloatField(null=True)
    bands = models.IntegerField(null=True)
    bands_order = models.CharField(max_length=50, default='3_2_1', help_text="Thứ tự kênh hình ảnh, ví dụ: 3_2_1, 1_2_3, 4_5_6")
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

class Topic(models.Model):
    TOPIC_TYPE_CHOICES = [
        ('BC_tin', 'BC tin'),
        ('Thong_tin_DTCB', 'Thông tin ĐTCB'),
        ('Chua_xac_dinh', 'Chưa xác định'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    topic_name = models.CharField(max_length=255, verbose_name="Topic Name")
    created_date = models.DateTimeField(default=datetime.now, verbose_name="Created Date")
    type = models.CharField(max_length=20, choices=TOPIC_TYPE_CHOICES, default='Chua_xac_dinh', verbose_name="Type")
    content = models.TextField(verbose_name="Content")
    area = models.CharField(max_length=255, verbose_name="Area")
    subject = models.CharField(max_length=255, verbose_name="Subject")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Created By")
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    class Meta:
        ordering = ['-created_date']
        verbose_name = "Topic"
        verbose_name_plural = "Topics"
    
    def __str__(self):
        return self.topic_name

class TopicAttachment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='attachments', verbose_name="Topic")
    file = models.FileField(upload_to='topic_attachments/', verbose_name="File")
    filename = models.CharField(max_length=255, verbose_name="Filename")
    file_size = models.BigIntegerField(verbose_name="File Size (bytes)")
    file_type = models.CharField(max_length=100, verbose_name="File Type")
    uploaded_at = models.DateTimeField(default=datetime.now, verbose_name="Uploaded At")
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = "Topic Attachment"
        verbose_name_plural = "Topic Attachments"
    
    def __str__(self):
        return f"{self.filename} - {self.topic.topic_name}"
    
    def save(self, *args, **kwargs):
        if not self.filename:
            self.filename = self.file.name.split('/')[-1]
        if not self.file_size:
            self.file_size = self.file.size
        if not self.file_type:
            self.file_type = self.file.name.split('.')[-1].upper()
        super().save(*args, **kwargs)
