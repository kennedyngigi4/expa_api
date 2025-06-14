# Generated by Django 5.1.7 on 2025-04-14 03:29

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Warehouse',
            fields=[
                ('wid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=255, null=True)),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('manager', models.CharField(blank=True, max_length=255, null=True)),
                ('email', models.EmailField(max_length=254, null=True)),
                ('phone', models.CharField(blank=True, max_length=30, null=True)),
                ('storage_type', models.CharField(blank=True, max_length=100, null=True)),
                ('total_storage', models.CharField(blank=True, max_length=100, null=True)),
                ('available_storage', models.CharField(blank=True, max_length=200, null=True)),
                ('loading_bays', models.CharField(blank=True, max_length=100, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('status', models.CharField(blank=True, max_length=60, null=True)),
                ('created_by', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
