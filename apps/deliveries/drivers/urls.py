from django.urls import path
from apps.deliveries.drivers.views import *


urlpatterns = [
    path( "shipments/", DriverAssignedShipmentsView.as_view(), name="shipments", ),
    path( "completed/", DriverCompletedShipmentsView.as_view(), name="completed", ),
    path( "shipment/<uuid:pk>/", DriverShipmentDetailView.as_view(), name="shipment", ),
    path( "shipments/<str:shipment_id>/update-status/", UpdateShipmentStatusView.as_view(), name="", ),
    path( "notifications/", DriverNotificationsView.as_view(), name="notifications", ),
]


