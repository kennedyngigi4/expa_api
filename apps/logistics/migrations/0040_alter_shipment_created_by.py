# Generated by Django 5.1.7 on 2025-05-10 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logistics', '0039_alter_shipment_partner_sharing_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shipment',
            name='created_by',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
