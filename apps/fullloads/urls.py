from django.urls import path
from apps.fullloads.views import *


urlpatterns = [
    path( "vehicle_types/", VehicleTypesView.as_view(), name="vehicle_types", ),
    path( "price_calculator/", CalculateFullloadPrice.as_view(), name="price_calculator", ),
]

