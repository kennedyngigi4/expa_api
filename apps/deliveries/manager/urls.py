from django.urls import path
from apps.deliveries.manager.views import *



urlpatterns = [
    path( "origin_packages/", ManagerOriginPackagesView.as_view(), name="origin_packages", ),
    path( "shipments/", ManagerCreateListShipmentView.as_view(), name="shipments", ),
    path( "incoming_shipments/", ManagerIncomingShipmentsView.as_view(), name="incoming_shipments", ),
]



