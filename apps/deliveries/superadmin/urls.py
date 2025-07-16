from django.urls import path
from apps.deliveries.superadmin.views import *


urlpatterns = [
    path( "intercounty_routes/", InterCountyRoutesView.as_view(), name="intercounty_routes", ),
    path("packages/", AllPackagesView.as_view(), name="packages", ),
    path("shipments/", AllShipmentsView.as_view(), name="shipments", ),
]



