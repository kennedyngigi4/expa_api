from django.contrib import admin
from apps.deliveries.models import *
# Register your models here.

admin.site.register(County)
admin.site.register(SizeCategory)
admin.site.register(PackageType)
admin.site.register(IntraCityParcelPolicy)
admin.site.register(InterCountyRoute)
admin.site.register(InterCountyWeightTier)
admin.site.register(LastMileDeliveryPolicy)
admin.site.register(UrgencyLevel)
admin.site.register(Package)
admin.site.register(Shipment)
admin.site.register(ShipmentStage)
admin.site.register(ShipmentPackage)
admin.site.register(ShipmentTracking)
admin.site.register(HandOver)
admin.site.register(IntraCityPackagePricing)
