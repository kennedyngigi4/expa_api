from django.utils import timezone
from django.db import transaction
from apps.deliveries.models import *

def create_intracity_shipment(package, courier, manager=None):
    with transaction.atomic():
        shipment = Shipment.objects.create(
            shipment_type="intra_city",
            manager=manager,
            courier=courier,
            status="assigned",
            origin_office=package.origin_office, 
            destination_office=package.destination_office,
            assigned_at=timezone.now()
        )


        # linking package to shipment
        ShipmentPackage.objects.create(
            shipment=shipment,
            package=package,
            status="assigned",
            pickup_address=package.sender_address,
            delivery_address=package.recipient_address,
            pickup_user=package.created_by
        )


        # Stage creation
        stage = ShipmentStage.objects.create(
            shipment=shipment,
            stage_number=1,
            driver=courier,
            status="assigned"
        )


        # update references
        sp = ShipmentPackage.objects.get(shipment=shipment, package=package)
        sp.pickup_stage = stage
        sp.delivery_stage = stage
        sp.save()

        return shipment




def create_inoffice_shipment(package, courier, manager=None):
    with transaction.atomic():
        shipment = Shipment.objects.create(
            shipment_type="in_office",
            manager=manager,
            courier=courier,
            status="assigned",
            origin_office=package.origin_office, 
            destination_office=package.destination_office,
            assigned_at=timezone.now()
        )


        # linking package to shipment
        ShipmentPackage.objects.create(
            shipment=shipment,
            package=package,
            status="assigned",
            pickup_address=package.sender_address,
            delivery_address=package.recipient_address,
            pickup_user=package.created_by
        )


        # Stage creation
        stage = ShipmentStage.objects.create(
            shipment=shipment,
            stage_number=1,
            driver=courier,
            status="assigned"
        )


        # update references
        sp = ShipmentPackage.objects.get(shipment=shipment, package=package)
        sp.pickup_stage = stage
        sp.delivery_stage = stage
        sp.save()

        return shipment
