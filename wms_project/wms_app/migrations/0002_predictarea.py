# Generated by Django 5.1.4 on 2025-01-06 18:00

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
                ('created_at', models.DateTimeField(default=datetime.datetime.now)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('geom', django.contrib.gis.db.models.fields.GeometryField(null=True, srid=4326)),
                ('image', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='predictions', to='wms_app.image')),
            ],
        ),
    ]
