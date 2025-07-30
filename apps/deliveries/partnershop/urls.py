from django.urls import path
from apps.deliveries.partnershop.views import *


urlpatterns = [
    path("packages/", PackageUploadView.as_view(), name="packages", ),
    path("intracity_pricing/", IntraCityPriceCalculationView.as_view(), name="intracity_pricing", ),
    path("intercounty_pricing/", InterCountyPriceCalculator.as_view(), name="intercounty_pricing", ),
]



