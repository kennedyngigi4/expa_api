# Generated by Django 5.2.3 on 2025-07-10 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(default='general', max_length=50),
        ),
    ]
