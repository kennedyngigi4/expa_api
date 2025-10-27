from django.urls import path
from apps.deliveries.views import *
from apps.deliveries.prints import generate_shipment_pdf, generate_package_pdf


urlpatterns = [
    path( "size_category/", SizeCategoryView.as_view(), name="size_category", ),
    path( "package_types/", PackageTypeView.as_view(), name="package_types", ),
    path( "urgency_types/", UrgencyView.as_view(), name="urgency_types", ),
    path( "business_stats/", BusinessAccountStatsView.as_view(), name="business_stats", ),

    path( "add_order/", AddOrderView.as_view(), name="add_order", ),
    path( "user_packages/", CustomerPackagesView.as_view(), name="user_packages", ),
    path( "user_package_details/<slug:slug>/", CustomerPackageRetrieveEditDeleteView.as_view(), name="user_package_details", ),
    path( "intracity_pricing/", IntraCityPriceCalculationView.as_view(), name="intracity_pricing", ),
    path( "intercounty_pricing/", InterCountyPriceCalculator.as_view(), name="intercounty_pricing"), 


    # print urls
    path("shipments/print/", generate_shipment_pdf, name="generate_shipment_pdf", ),
    path("packages/print/", generate_package_pdf, name="generate_package_pdf", ),
]

