from rest_framework import serializers
from apps.deliveries.models import *



class ShipmentPackageSummarySerializer(serializers.ModelSerializer):
    package_id = serializers.CharField(source='package.package_id')
    pickup_address = serializers.CharField(source='package.sender_address')
    pickup_latLng = serializers.CharField(source='package.sender_latLng')
    recipient_name = serializers.CharField(source='package.recipient_name')
    recipient_address = serializers.CharField(source='package.recipient_address')
    recipient_latLng = serializers.CharField(source='package.recipient_latLng')
    status = serializers.CharField()

    class Meta:
        model = ShipmentPackage
        fields = ["package_id", "pickup_address", "pickup_latLng", "recipient_name", "recipient_address", 'recipient_latLng', "status"]



class RiderShipmentSerializer(serializers.ModelSerializer):
    shipment_type = serializers.CharField(source="get_shipment_type_display")
    summary = serializers.SerializerMethodField()
    stage_number = serializers.SerializerMethodField()
    stage_status = serializers.SerializerMethodField()
    handover_required = serializers.SerializerMethodField()
    handover_completed = serializers.SerializerMethodField()
    delivered_packages = serializers.SerializerMethodField()
    total_packages = serializers.SerializerMethodField()
    origin_office = serializers.CharField(source='origin_office.name', read_only=True)
    destination_office = serializers.CharField(source='destination_office.name', read_only=True)
    packages = ShipmentPackageSummarySerializer(many=True, source="shipmentpackage_set", read_only=True)


    class Meta:
        model = Shipment
        fields = [
            "shipment_id",
            "shipment_type",
            "summary",
            "stage_number",
            "stage_status",
            "handover_required",
            "handover_completed",
            "status",
            "delivered_packages",
            "total_packages",
            "origin_office",
            "destination_office",
            "packages",
        ]

    def get_summary(self, obj):
        packages = obj.shipmentpackage_set.all()
        if obj.shipment_type == "pickup":
            sources = set(p.package.sender_address for p in packages)
            if obj.origin_office:
                return f"Pickup from {len(sources)} client(s) to {obj.origin_office.name}"
            else:
                return f"Pickup from {len(sources)} client(s)"
        
        elif obj.shipment_type == "delivery":
            destinations = set(p.package.recipient_address for p in packages)
            return f"Delivery from {obj.origin_office.name} to {len(destinations)} client(s)"
        elif obj.shipment_type == "transfer":
            return f"Transfer from {obj.origin_office.name} to {obj.destination_office.name}"
        elif obj.shipment_type == "complete":
            return f"{len(packages)} direct delivery(s)"
        return "Shipment"
    

    def get_stage_number(self, obj):
        user = self.context['request'].user
        stage = obj.stages.filter(driver=user).first()
        return stage.stage_number if stage else None

    def get_stage_status(self, obj):
        user = self.context['request'].user
        stage = obj.stages.filter(driver=user).first()
        return stage.status if stage else None

    def get_handover_required(self, obj):
        user = self.context['request'].user
        stage = obj.stages.filter(driver=user).first()
        return stage.handover_required if stage else None

    def get_handover_completed(self, obj):
        user = self.context['request'].user
        stage = obj.stages.filter(driver=user).first()
        return bool(stage.completed_at) if stage else False

    def get_delivered_packages(self, obj):
        return obj.shipmentpackage_set.filter(status='delivered').count()

    def get_total_packages(self, obj):
        return obj.shipmentpackage_set.count()





