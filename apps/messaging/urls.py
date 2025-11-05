from django.urls import path
from apps.messaging.views import *

urlpatterns = [
    path("notifications/", NotificationsView.as_view(), name="otifications", ),
]


