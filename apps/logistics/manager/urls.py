from django.urls import path
from apps.logistics.manager.views import *

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'shipments', ShipmentsViewSet, basename="shipments", ),
urlpatterns = router.urls

urlpatterns += [
    path( "statistics/", ManagerStatisticsView.as_view(), name="statistics", ),
    path( "create_order/", ManagerCreateOrder.as_view(), name="create_order", ),
    path("orders/", ClassifiedOrdersListView.as_view(), name="orders", ),
    path( "order_details/<str:pk>", OrderDetailsView.as_view(), name="order_details", ),
    path( "order_update/<str:pk>/", UpdateOrderView.as_view(), name="order_update", ),
    path( "orderdetails_update/<str:pk>/", OrderDetailsUpdateView.as_view(), name="orderdetails_update", ),
    path( "invoices/", ManagerInvoicesView.as_view(), name="invoices", ),
    path( "create_pickup/", CreatePickupShipmentView.as_view(), name="create_pickup", ),
    path( "delete_shipment_item/<str:pk>/", ShipmentItemDeleteView.as_view(), name="delete_shipment_item", ),
    path( "shipment_leg/", ShipmentLegView.as_view(), name="shipment_leg", ),
    path( "delete_shipment_leg/<str:pk>/", DeleteShipmentLegView.as_view(), name="delete_shipment_leg", ),
    path( "incidents/", ManagerShipmentIncidentsView.as_view(), name="incidents", ),
]



