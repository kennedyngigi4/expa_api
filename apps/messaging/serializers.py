from rest_framework import serializers
from apps.messaging.models import *

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id", "subject", "message", "sent_to", "tracking", "created_by", "created_at", "is_read"
        ]



