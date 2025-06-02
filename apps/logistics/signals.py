from django.dispatch import receiver
from django.db.models.signals import post_save
from apps.logistics.models import *
from apps.accounts.models import *
from apps.messaging.models import *
from core.message_constants import *
from apps.messaging.views import SendNotification

@receiver(post_save, sender=Order)
def OrderDetailsSignal(sender, instance, created, *args, **kwargs):
    if created:

        # Save details of the order
        details = OrderDetails.objects.create(order=instance)
        details.save()


        # Generate invoice if user has account
        creator = User.objects.get(uid=instance.created_by)
        # account_type = Profile.objects.get(user=creator)

        



@receiver(post_save, sender=OrderDetails)
def assignmentNotification(sender, instance, created, *args, **kwargs):
    # this is a notification generator to both client and courier
    if not created:
        if instance.delivery_status == "ASSIGNED":
            # driver =  Notification.objects.create(
            #     sent_to=instance.assigned_pickupto,
            #     subject=driver_pickup_subject,
            #     message=driver_pickup_message,
            #     tracking=instance.order.order_id,
            # )
            # driver.save()
            SendNotification(instance.assigned_pickupto, driver_pickup_subject, driver_pickup_message, instance.order.order_id)


            # Sending notification to client
            # client = Notification.objects.create(
            #     sent_to=instance.order.created_by,
            #     subject=client_pickup_subject,
            #     message=client_pickup_message,
            #     tracking=instance.order.order_id,
            # )
            # client.save()
            SendNotification(instance.order.created_by, client_pickup_subject, client_pickup_message, instance.order.order_id)




