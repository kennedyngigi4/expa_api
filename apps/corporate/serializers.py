import json
from rest_framework import serializers
from collections import defaultdict

from apps.corporate.models import *
from apps.accounts.models import *
from apps.deliveries.models import Package, PackageItem, PackageAttachment


class PackageItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageItem
        fields = [
            "destination", "destination_latLng", "weight", "description", "price"
        ]


class PackageAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageAttachment
        fields = [
            "id","package", "attachment"
        ]


class CorpPackageWriteSerializer(serializers.ModelSerializer):
    package_items = serializers.JSONField(write_only=True, required=False)

    class Meta:
        model = Package
        fields = [
            "name", "package_type", "size_category", "delivery_type", "is_fragile", "urgency", "weight", "pickup_date", 
            "description", "sender_name", "sender_phone", "sender_address", "sender_latLng", "is_paid", "recipient_name",
            "recipient_phone", "recipient_address", "recipient_latLng", "package_id", "status", "requires_last_mile", 
            "requires_pickup", "fees", "vehicle_type", "package_items", "requires_packaging"
        ]
        extra_kwargs = {
            "sender_name": {"required": False},
            "sender_phone": {"required": False},
            "sender_address": {"required": False},
            "sender_latLng": {"required": False},
        }

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user
        
        office = getattr(user, "corporate_office", None)

        if office:
            validated_data.setdefault("sender_name", office.name)
            validated_data.setdefault("sender_phone", office.phone)
            validated_data.setdefault("sender_address", office.address)
            validated_data.setdefault("sender_latLng", office.lat_lng)

        # JSONField already parses the JSON string
        items_data = validated_data.pop("package_items", [])

        package = Package.objects.create(**validated_data)

        for item_data in items_data:
            obj = PackageItem.objects.create(package=package, **item_data)
            print("CREATED ITEM >>>", obj.id)

        return package


class CorpPackageReadSerializer(serializers.ModelSerializer):
    package_items = PackageItemsSerializer(many=True, required=False)
    package_attachments = PackageAttachmentSerializer(many=True, required=False)
    urgency_name = serializers.SerializerMethodField()
    package_type_name = serializers.SerializerMethodField()

    class Meta:
        model = Package
        fields = [
            "slug","name", "package_type", "package_type_name", "size_category", "delivery_type", "is_fragile", "urgency", "urgency_name", "weight", "pickup_date", 
            "description", "sender_name", "sender_phone", "sender_address", "sender_latLng", "is_paid", "recipient_name",
            "recipient_phone", "recipient_address", "recipient_latLng", "package_id", "status", "requires_last_mile", 
            "requires_pickup", "fees", "vehicle_type", "package_items", "package_attachments", "requires_packaging"
        ]
        
    def get_urgency_name(self, obj):
        if obj.urgency:
            return obj.urgency.name
        return None


    def get_package_type_name(self, obj):
        return getattr(obj.package_type, "name", None)


