from rest_framework import serializers
from apps.fullloads.models import *


class VehicleTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleType
        fields = [
            "id", "name", "description"
        ]


class BookingWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            "id", "sender", "vehicle", "pickup_address", "dropoff_address", "distance", "price", "weight", "created_at" 
        ]

        read_only_fields = [
            "id", "sender", "created_at" 
        ]



