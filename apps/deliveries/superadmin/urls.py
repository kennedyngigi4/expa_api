from django.urls import path
from apps.deliveries.superadmin.views import *


urlpatterns = [
    path("packages/", AllPackagesView.as_view(), name="packages", ),
    path("shipments/", AllShipmentsView.as_view(), name="shipments", ),
]



