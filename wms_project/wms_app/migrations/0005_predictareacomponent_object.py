# Generated by Django 5.1.4 on 2025-02-24 09:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wms_app', '0004_alter_predictareacomponent_area'),
    ]

    operations = [
        migrations.AddField(
            model_name='predictareacomponent',
            name='object',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
