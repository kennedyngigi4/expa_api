from django.urls import path
from apps.messaging.views import *

urlpatterns = [
    path("notifications/", UserNotifications.as_view(), name="notifications", ),
]

