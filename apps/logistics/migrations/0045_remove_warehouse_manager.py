# Generated by Django 5.1.7 on 2025-05-23 09:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('logistics', '0044_orderdetails_invoice_id_orderdetails_is_invoiced'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='warehouse',
            name='manager',
        ),
    ]
