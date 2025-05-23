# Generated by Django 5.1.2 on 2024-10-29 03:50

import datetime
import django.contrib.gis.db.models.fields
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('datetime', models.DateTimeField(null=True)),
                ('resolution', models.FloatField(null=True)),
                ('bands', models.IntegerField(null=True)),
                ('filename', models.CharField(max_length=255, null=True)),
                ('filepath', models.CharField(max_length=1000, null=True)),
                ('area', models.FloatField(null=True)),
                ('name', models.CharField(max_length=255, null=True)),
                ('topic', models.CharField(max_length=255, null=True)),
                ('source', models.CharField(max_length=255, null=True)),
                ('satellite_id', models.CharField(max_length=255, null=True)),
                ('geom', django.contrib.gis.db.models.fields.GeometryField(null=True, srid=4326)),
            ],
        ),
    ]
