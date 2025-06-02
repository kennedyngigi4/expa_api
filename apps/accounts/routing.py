from django.urls import re_path
from apps.accounts import consumers



websocket_urlpatterns = [
    re_path(r"ws/driver-location/", consumers.DriverLocationConsumer.as_asgi()),
]




