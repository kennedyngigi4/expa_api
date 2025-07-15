from django.urls import path
from apps.messaging.partnershop.views import *

urlpatterns = [
    path("notifications/", NotificationsView.as_view(), name="notifications", )
]


