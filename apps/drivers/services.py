from django.utils import timezone
from django.db import transaction
from apps.deliveries.models import *

def create_intracity_shipment(package, courier, manager=None):
    with transaction.atomic():
        shipment = Shipment.objects.create(
            shipment_type="complete",
            manager=manager,
            courier=courier,
            status="created",
            assigned_at=timezone.now()
        )


        # linking package to shipment
        ShipmentPackage.objects.create(
            shipment=shipment,
            package=package,
            status="pending",
            pickup_address=package.sender_address,
            delivery_address=package.recipient_address,
            pickup_user=package.created_by
        )


        # Stage creation
        stage = ShipmentStage.objects.create(
            shipment=shipment,
            stage_number=1,
            driver=courier,
            status="pending"
        )


        # update references
        sp = ShipmentPackage.objects.get(shipment=shipment, package=package)
        sp.pickup_stage = stage
        sp.delivery_stage = stage
        sp.save()

        return shipment
