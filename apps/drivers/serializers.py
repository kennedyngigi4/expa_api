from rest_framework import serializers
from apps.accounts.models import *
from apps.deliveries.models import *
from apps.drivers.models import *


class DriverLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverLocation
        fields = ["id", "driver", "latitude", "longitude", "updated_at"]
        read_only_fields = ["id", "updated_at", "driver"]


    def create(self, validated_data):
        
        request = self.context.get("request")

        if request and hasattr(request, "user"):
            validated_data["driver"] = request.user

        return super().create(validated_data)




class DriverOrderDetails(serializers.ModelSerializer):
    size_category_name = serializers.SerializerMethodField()
    urgency_name = serializers.SerializerMethodField()
    package_type_name = serializers.SerializerMethodField()
    origin_office = serializers.SerializerMethodField()
    destination_office = serializers.SerializerMethodField()

    class Meta:
        model = Package
        fields = [
            "id","slug","name", "package_type", "package_type_name", "size_category", "size_category_name", "delivery_type", "is_fragile", 
            "urgency", "urgency_name","length", "width", "height", "weight", "pickup_date", "description", "sender_name", "sender_phone", 
            "sender_address", "sender_latLng", "is_paid", "recipient_name", "recipient_phone", "recipient_address", "recipient_latLng", 
            "package_id", "status", "created_by_role", "created_at", "origin_office", "destination_office"
        ]
        

    def get_origin_office(self, obj):
        return obj.origin_office.address
    
    def get_destination_office(self, obj):
        return obj.destination_office.address

    def get_size_category_name(self, obj):
        if obj.size_category:
            return obj.size_category.name
        return None
    
    def get_urgency_name(self, obj):
        if obj.urgency:
            return obj.urgency.name
        return None
    
    def get_package_type_name(self, obj):
        return getattr(obj.package_type, "name", None)




class DriverShipmentSerializer(serializers.ModelSerializer):
    package = serializers.SerializerMethodField()
    qrcode_svg = serializers.SerializerMethodField()

    class Meta:
        model = Shipment
        fields = [
            "id","shipment_id","shipment_type", "packages", "origin_office", "destination_office", "status", "courier", "requires_handover", 
            "pickup_location", "pickup_latLng", "destination_location", "destination_latLng", "package", "assigned_at", "qrcode_svg",
        ]

    def get_qrcode_svg(self, obj):
        request = self.context.get("request")
        if obj.qrcode_svg:
            return request.build_absolute_uri(obj.qrcode_svg.url)
        return None
    

    def get_package(self, obj):
        package = obj.packages.first()
        return DriverOrderDetails(package).data if package else None





class WalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = [
            "id",
            "amount",
            "transaction_type",
            "status",
            "note",
            "created_at",
        ]
