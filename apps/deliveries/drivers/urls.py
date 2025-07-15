from django.urls import path
from apps.deliveries.drivers.views import *


urlspattern = [
    path("shipments/", DriversAllShipments.as_view(), name="shipments", ),
    path( "shipment/<uuid:pk>/", DriverShipmentDetailView.as_view(), name="shipment", ),
]


