from django.urls import path
from apps.fullloads.manager.views import *


urlpatterns = [
    path("fullloads/", AllOfficeFullloadsView.as_view(), name="fullloads", ),
]

