# Generated by Django 5.1.4 on 2025-03-08 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wms_app', '0005_predictareacomponent_object'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='format',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
