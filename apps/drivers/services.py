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
            pickup_location=package.sender_address,
            pickup_latLng=package.sender_latLng, 
            destination_location=package.recipient_address,
            destination_latLng=package.recipient_latLng,
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
            shipment_type="pickup",
            manager=manager,
            courier=courier,
            status="assigned",
            pickup_location=package.sender_address,
            pickup_latLng=package.sender_latLng, 
            destination_office=package.origin_office,
            destination_location=package.origin_office.address,
            destination_latLng=f"{package.origin_office.geo_lat},{package.origin_office.geo_lng}",
            assigned_at=timezone.now() 
        )


        # linking package to shipment
        ShipmentPackage.objects.create(
            shipment=shipment,
            package=package,
            status="assigned",
            pickup_address=package.sender_address,
            delivery_address=package.origin_office.address,
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
