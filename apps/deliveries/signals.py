from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.accounts.models import *
from apps.deliveries.models import *
from apps.payments.models import Invoice
from apps.messaging.models import Notification
from decimal import Decimal


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
