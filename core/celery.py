import os
from celery import Celery



os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'core.settings')
app = Celery('core')


# load settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# autodiscover tasks.py in all apps
app.autodiscover_tasks()

