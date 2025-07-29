from django.urls import path
from apps.deliveries.drivers.views import *


urlpatterns = [
    path("shipments/", DriverAssignedShipmentsView.as_view(), name="shipments", ),
    path( "shipment/<uuid:pk>/", DriverShipmentDetailView.as_view(), name="shipment", ),
]


