import uuid
from django.db import models

# Create your models here.


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    subject = models.CharField(max_length=255, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    sent_to = models.CharField(max_length=255, null=True, blank=True)
    tracking = models.CharField(max_length=255, null=True, blank=True)
    created_by = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return str(self.subject)



