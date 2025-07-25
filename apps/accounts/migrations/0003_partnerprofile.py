# Generated by Django 5.2.3 on 2025-06-30 11:41

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_user_date_joined_alter_user_last_login'),
    ]

    operations = [
        migrations.CreateModel(
            name='PartnerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('business_name', models.CharField(max_length=255)),
                ('license_number', models.CharField(blank=True, max_length=100)),
                ('id_document', models.FileField(upload_to='partner_ids/')),
                ('is_verified', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='partner_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
