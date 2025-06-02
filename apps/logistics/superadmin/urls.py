from django.urls import path
from apps.logistics.superadmin.views import *
from apps.logistics.views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'warehouses', WarehouseViewset, basename='warehouses', ),
router.register(r'routes', RouteView, basename="routes", ),
urlpatterns = router.urls


urlpatterns += [
    path("statistics/", StatisticsView.as_view(), name="statistics", ),
    path( "courier/<str:driver_id>/shipments/", CourierShipmentListView.as_view()),
    path( "orders/", OrdersView.as_view(), name="orders", ),
    path( "client/<str:client_id>/orders/", ClientOrdersListView.as_view()),
    path( "order_details/<str:pk>/", OrderDetailsView.as_view(), name="order_details", ),
    path( "deliveries/", AllDeliveriesView.as_view(), name="deliveries", ),
    path( "delivery_details/<str:pk>/", DeliveryDetailsView.as_view(), name="delivery_details", ),
    path( "warehouse_employees/<str:pk>/", WarehouseEmployeesView.as_view(), name="warehouse_employees", )
]



