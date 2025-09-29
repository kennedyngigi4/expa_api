from rest_framework import serializers
from apps.messaging.models import *



class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [ 
            "id","title", "message", "notification_type", "is_read", "created_at", "package", "shipment"
        ]


