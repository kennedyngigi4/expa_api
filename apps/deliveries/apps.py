from django.apps import AppConfig


class DeliveriesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.deliveries'


    def ready(self):
        import apps.deliveries.signals



