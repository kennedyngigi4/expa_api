from rest_framework import serializers
from apps.fullloads.models import *


class VehicleTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleType
        fields = [
            "id", "name", "description"
        ]
