# Generated by Django 5.2.3 on 2025-07-14 14:12

import apps.deliveries.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deliveries', '0017_shipmentstage_handover_required'),
    ]

    operations = [
        migrations.AlterField(
            model_name='package',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=apps.deliveries.models.UserPackageImgPath, verbose_name='package image'),
        ),
    ]
