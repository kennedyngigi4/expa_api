from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.accounts.models import *
from apps.deliveries.models import *
from apps.drivers.views import get_nearby_drivers
from apps.payments.models import Invoice
from apps.messaging.models import Notification
from apps.messaging.views import *
from decimal import Decimal


@receiver(post_save, sender=Package)
def send_intracity_notifications_to_drivers(sender, instance, created, **kwargs):
    if created and instance.delivery_type == "intra_city":
        print("Signal triggered for package:", instance.id)

        if not instance.sender_latLng:
            print("No sender_latLng, skipping...")
            return

        try:
            lat, lng = instance.sender_latLng.split(",")
            pickup_coords = (float(lat.strip()), float(lng.strip()))
        except ValueError:
            print("Invalid latLng format:", instance.sender_latLng)
            return

        nearby_drivers = get_nearby_drivers(pickup_coords, radius_km=5)
        print("Nearby drivers found:", nearby_drivers)

        if nearby_drivers:
            intracity_drivers_notification(
                drivers=nearby_drivers,  # now proper driver objects
                title="🚚 New Intracity Order",
                body=f"Pickup at {instance.sender_latLng}",
                data={"type": "new_order", "order_id": str(instance.id)},
            )
            print("Sent >>>>>>>>>>>>>>>>")
        else:
            print("No nearby drivers")



@receiver(post_save, sender=Package)
def create_invoice(sender, instance, created, **kwargs):
    if not created:
        return
    
    user = instance.created_by
    if hasattr(instance, 'invoice'):
        return
    
    status = 'unpaid' if user.account_type == "personal" else 'pending'
    invoice = Invoice.objects.create(
        user=user,
        package=instance,
        amount=Decimal(round(instance.fees, 3)),
        status=status
    )

    
@receiver(post_save, sender=Package)
def notify_on_partner_upload(sender, instance, created, **kwargs):
    user = instance.created_by

    if not created or user.role != "partner_shop":
        return
    
    office = instance.origin_office
    package = instance

    # Notify office personel
    managers = User.objects.filter(role="manager", office=office)
    for manager in managers:
        Notification.objects.create(
            user=manager,
            title=f"New Partner Package - {package.package_id}",
            message=f"{user.full_name} uploaded a package at {office.name}.",
            package=package
        )

    # Notify the creator
    Notification.objects.create(
        user=user,
        title=f"{package.package_id} Upload Confirmed",
        message=f"Your package, {package.package_id} to {office.name} was uploaded successfully.",
        package=package
    )



@receiver(post_save, sender=Shipment)
def notify_assigned_courier(sender, instance, created, **kwargs):
    if created and instance.courier:
        Notification.objects.create(
            user=instance.courier,
            title=f"New Shipment Assigned - {instance.shipment_id}",
            message=f"You have been assigned a new shipment: {instance.shipment_id}. Shipment type: {instance.shipment_type} at {instance.origin_office}.",
            shipment=instance,
            notification_type="assignment",
        )
