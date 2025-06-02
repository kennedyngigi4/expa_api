from django.dispatch import receiver
from django.db.models.signals import post_save
from apps.accounts.models import User, Profile, DriverLocation




@receiver(post_save, sender=User)
def profileDriverSignal(sender, created, instance=None, **kwargs):
    if created:
        if instance.role == "Client":
            Profile.objects.create(user=instance, account_type="Personal")

        elif instance.role == "Agent":
            Profile.objects.create(user=instance)

        elif instance.role == "Driver":
            DriverLocation.objects.create(driver=instance)


