# Generated by Django 5.1.7 on 2025-05-21 10:33

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0004_remove_invoice_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='order',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.UUIDField(), blank=True, default=list, null=True, size=None),
        ),
    ]
