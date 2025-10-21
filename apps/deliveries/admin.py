from django.contrib import admin
from django.db.models import Q
from apps.deliveries.models import *
from django.core.exceptions import ValidationError
# Register your models here.

admin.site.register(County)
admin.site.register(SizeCategory)
admin.site.register(PackageType)
admin.site.register(IntraCityParcelPolicy)
admin.site.register(LastMileDeliveryPolicy)
admin.site.register(UrgencyLevel)
admin.site.register(Package)
admin.site.register(PackageAttachment)
admin.site.register(PackageItem)
admin.site.register(Shipment)
admin.site.register(ShipmentStage)
admin.site.register(ShipmentPackage)
admin.site.register(ShipmentTracking)
admin.site.register(ProofOfDelivery)
admin.site.register(HandOver)
admin.site.register(IntraCityPackagePricing)



@admin.register(InterCountyRoute)
class InterCountyRouteAdmin(admin.ModelAdmin):
    list_display = ("__str__", "base_price", "base_weight_limit", "size_category")
    search_fields = ("origins__name", "destinations__name")
    filter_horizontal = ("origins", "destinations")

    def save_related(self, request, form, formsets, change):
        """
        After the M2M fields are saved, check for reverse duplicates.
        """
        super().save_related(request, form, formsets, change)

        route = form.instance
        origins = list(route.origins.all())
        destinations = list(route.destinations.all())

        for origin in origins:
            for destination in destinations:
                existing = InterCountyRoute.objects.filter(
                    size_category=route.size_category
                ).filter(
                    Q(origins=origin, destinations=destination)
                    | Q(origins=destination, destinations=origin)
                ).exclude(id=route.id).first()

                if existing:
                    raise ValidationError(
                        f"A reverse route already exists: {existing}. "
                        "Please edit that route instead of creating a new one."
                    )


@admin.register(InterCountyWeightTier)
class InterCountyWeightTierAdmin(admin.ModelAdmin):
    list_display = ("route", "min_weight", "max_weight", "price_per_kg")


