from django.contrib import admin
from apps.logistics.models import *
# Register your models here.

admin.site.register(Order)
admin.site.register(OrderDetails)
admin.site.register(OrderImages)
admin.site.register(Warehouse)
admin.site.register(Shipment)
admin.site.register(ShipmentItems)
admin.site.register(ShipmentLeg)
admin.site.register(Route)
admin.site.register(Incident)


