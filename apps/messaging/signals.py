from django.dispatch import receiver
from django.db.models.signals import post_save

from apps.accounts.models import *
from apps.logistics.models import *
from apps.payments.models import *
from apps.messaging.models import *

from core.message_constants import *


@receiver(post_save, sender=Order)
def OrderCreationSignal(sender, created, instance=None, **kwargs):
    if created:
        notification = Notification.objects.create(
            subject=order_success_subject,
            message=order_success_message,
            sent_to=instance.created_by,
            tracking=instance.order_id,
            created_by=instance.created_by
        )

        notification.save()




