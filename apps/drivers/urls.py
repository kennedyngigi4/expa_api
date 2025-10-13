from django.urls import path
from apps.drivers.views import *


urlpatterns = [
    path("statistics/", DriverStatistics.as_view(), name="statistics", ),
    path("stream-location/", DriverLocationUpdate.as_view(), name="stream-location"),
    path("register-token/", RegisterFCMToken.as_view(), name="register-token"),
    path("order-details/<str:order_id>/", GetOrderDetailsView.as_view(), name="order-details", ),
    path("accept-delivery/", AcceptDeliveryView.as_view(), name="accept-delivery", ),
    path("shipment-details/<str:shipment_id>/", ShipmentDetailsUpdatesView.as_view(), name="shipment-details", ),
    path("incomplete-shipments/", DriverIncompleteShipmentsView.as_view(), name="incomplete-shipments", ),
    path("completed-shipments/", DriverCompletedShipmentsView.as_view(), name="completed-shipments", ),
    path("shipment/<str:shipment_id>/update-status/", ShipmentUpdateStatusView.as_view(), name="shipment-update-status", ),
    path("rider-withdraw/", WithdrawalWalletView.as_view(), name="rider-withdraw"),
    path("rider-transactions/", RiderWalletTransactionsView.as_view(), name="rider-transactions", ),
]


