from django.urls import path
from apps.messaging.views import *

urlpatterns = [
    path("customer_notifications/", ClientNotificationsView.as_view(), name="customer_notifications", )
]


