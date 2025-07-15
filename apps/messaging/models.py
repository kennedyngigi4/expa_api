from django.db import models
from apps.accounts.models import *
from apps.deliveries.models import *
# Create your models here.



class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    package = models.ForeignKey(Package, null=True, blank=True, on_delete=models.CASCADE)
    shipment = models.ForeignKey(Shipment, null=True, blank=True, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=50, default='general')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.email}"



