# Generated by Django 5.1.7 on 2025-05-08 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logistics', '0034_shipment_shipment_route'),
    ]

    operations = [
        migrations.AddField(
            model_name='shipment',
            name='shipment_type',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
