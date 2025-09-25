from django.dispatch import receiver
from django.db.models.signals import post_save
from apps.accounts.models import User, PartnerProfile
from apps.drivers.models import Wallet

@receiver(post_save, sender=User)
def create_partner_profile(created, instance, **kwargs):
    print(instance.role)
    if created and instance.role in ['partner_shop' ]:
        PartnerProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def create_partnerrider_wallet(created, instance, **kwargs):
    if created and instance.role in ['partner_rider']:
        Wallet.objects.get_or_create(user=instance)



