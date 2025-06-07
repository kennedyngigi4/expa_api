from django.urls import path
from apps.accounts.courier.views import *


urlpatterns = [
    path("location_stream/", CourierLocationStreamView.as_view(), name="location_stream", ),
]




