# Generated by Django 5.1.7 on 2025-05-14 10:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logistics', '0041_shipmentitems_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='shipmentleg',
            name='completedtime',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='shipmentleg',
            name='starttime',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
