# Generated migration for adding bands_order field to Image model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wms_app', '0008_topic_topicattachment'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='bands_order',
            field=models.CharField(default='3_2_1', help_text='Thứ tự kênh hình ảnh, ví dụ: 3_2_1, 1_2_3, 4_5_6', max_length=50),
        ),
    ]
