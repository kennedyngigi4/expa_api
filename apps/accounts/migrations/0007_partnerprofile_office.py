# Generated by Django 5.2.3 on 2025-07-11 22:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_office_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='partnerprofile',
            name='office',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.office'),
        ),
    ]
