# Generated by Django 5.1.4 on 2025-02-23 23:32

import datetime
import django.contrib.gis.db.models.fields
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wms_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PredictArea',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('image', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='predictions', to='wms_app.image')),
            ],
        ),
        migrations.CreateModel(
            name='PredictAreaComponent',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('options', models.CharField(max_length=10000, null=True)),
                ('geom', django.contrib.gis.db.models.fields.GeometryCollectionField(null=True, srid=4326)),
                ('area', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='components', to='wms_app.predictarea')),
            ],
        ),
    ]
