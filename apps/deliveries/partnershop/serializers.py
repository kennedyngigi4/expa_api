from rest_framework import serializers
from apps.deliveries.models import *


class PackageWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Package
        fields = [
            "slug","name", "package_type", "size_category", "delivery_type", "is_fragile", "urgency",
            "length", "width", "height", "weight", "pickup_date", "description", "sender_name", "sender_phone", 
            "is_paid", "recipient_name", "recipient_phone", "recipient_address", "recipient_latLng", 
            "package_id", "status", "requires_last_mile", "fees"
        ]
        


