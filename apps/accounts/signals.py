from django.dispatch import receiver
from django.db.models.signals import post_save
from apps.accounts.models import User, PartnerProfile


@receiver(post_save, sender=User)
def create_partner_profile(created, instance, **kwargs):
    print(instance.role)
    if created and instance.role in [ 'partner_rider', 'partner_shop' ]:
        PartnerProfile.objects.get_or_create(user=instance)


