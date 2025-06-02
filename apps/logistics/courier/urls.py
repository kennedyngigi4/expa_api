from django.urls import path
from apps.logistics.courier.views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"incidents", IncidentViewSet, basename="incidents", ),
urlpatterns = router.urls

urlpatterns += [
    path( "pickups/", AssignedPickupsView.as_view(), name="pickups", ),
    path( "shipments/", DriverShipmentView.as_view(), name="shipments", ),
    path( "start_delivery/", StartDeliveryView.as_view(), name="start_delivery", ),
    path( "deliveries/", AssignedDeliveriesView.as_view(), name="deliveries", ),
    path( "notifications/", CourierNotificationsView.as_view(), name="notifications", ),
]


