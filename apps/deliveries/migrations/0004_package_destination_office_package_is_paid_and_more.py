# Generated by Django 5.2.3 on 2025-07-08 06:52

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_user_phone'),
        ('deliveries', '0003_county_intracitypricingrule_sizecategory_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='package',
            name='destination_office',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='destination_packages', to='accounts.office'),
        ),
        migrations.AddField(
            model_name='package',
            name='is_paid',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='package',
            name='is_returned',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='package',
            name='origin_office',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='origin_packages', to='accounts.office'),
        ),
        migrations.AddField(
            model_name='package',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('assigned', 'Assigned'), ('in_transit', 'In Transit'), ('delivered', 'Delivered'), ('returned', 'Returned'), ('cancelled', 'Cancelled')], default='pending', max_length=30),
        ),
        migrations.AddIndex(
            model_name='package',
            index=models.Index(fields=['created_by'], name='deliveries__created_519069_idx'),
        ),
        migrations.AddIndex(
            model_name='package',
            index=models.Index(fields=['sender_user'], name='deliveries__sender__ce26d4_idx'),
        ),
        migrations.AddIndex(
            model_name='package',
            index=models.Index(fields=['delivery_type'], name='deliveries__deliver_2b3e51_idx'),
        ),
        migrations.AddIndex(
            model_name='package',
            index=models.Index(fields=['created_at'], name='deliveries__created_044f72_idx'),
        ),
        migrations.AddIndex(
            model_name='package',
            index=models.Index(fields=['status'], name='deliveries__status_adf528_idx'),
        ),
    ]
