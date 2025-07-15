from rest_framework import serializers
from apps.deliveries.models import PackageType, Package, Shipment, SizeCategory, ShipmentPackage, ShipmentTracking, HandOver, UrgencyLevel, ShipmentStage
from apps.messaging.models import Notification




class SizeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SizeCategory
        fields = [
            "id","name", "max_length", "max_width", "max_height", "description", "base_price"
        ]


class PackageTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageType
        fields = [
            'id', 'name', 'price'
        ]


class UrgencyLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = UrgencyLevel
        fields = [
            "id", "name", "description", "surcharge_type", "surcharge_amount"
        ]



class PackageWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Package
        fields = [
            "slug","name", "package_type", "size_category", "delivery_type", "is_fragile", "urgency",
            "length", "width", "height", "weight", "pickup_date", "description", "sender_name", "sender_phone", "sender_address", 
            "sender_latLng", "is_paid", "recipient_name", "recipient_phone", "recipient_address", "recipient_latLng", 
            "package_id", "status", "requires_last_mile", "requires_pickup", "fees"
        ]
        read_only_fields = [
            "id", "package_id", "current_handler", "delivery_stage_count", "current_stage"
        ]


class PackageSerializer(serializers.ModelSerializer):

    size_category_name = serializers.SerializerMethodField()
    urgency_name = serializers.SerializerMethodField()
    package_type_name = serializers.SerializerMethodField()

    class Meta:
        model = Package
        fields = [
            "id","slug","name", "package_type", "package_type_name", "size_category", "size_category_name", "delivery_type", "is_fragile", "urgency", "urgency_name",
            "length", "width", "height", "weight", "pickup_date", "description", "sender_name", "sender_phone", "sender_address", 
            "sender_latLng", "is_paid", "recipient_name", "recipient_phone", "recipient_address", "recipient_latLng", 
            "package_id", "status"
        ]
        read_only_fields = [
            "id", "package_id", "current_handler", "delivery_stage_count", "current_stage"
        ]


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





class ShipmentSerializer(serializers.ModelSerializer):
    packages = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True
    )

    class Meta:
        model = Shipment
        fields = [
            "shipment_id","shipment_type", "packages", "origin_office", "destination_office", "status", "courier", "requires_handover"
        ]


    def create(self, validated_data):
        request = self.context["request"]
        manager = request.user
        packages_data = validated_data.pop("packages", [])

        if not validated_data.get("origin_office") and hasattr(manager, 'office'):
            validated_data["origin_office"] = manager.office

        shipment = Shipment.objects.create(manager=manager, **validated_data)

        for package_id in packages_data:
            try:
                package = Package.objects.get(id=package_id)
                ShipmentPackage.objects.create(shipment=shipment, package=package)

                # Update package status (e.g. to "assigned")
                package.status = "assigned"
                package.save()

                # Optional: Send notification
                self.send_package_notification(package)
            except Package.DoesNotExist:
                continue


        # Initial ShipmentStage
        ShipmentStage.objects.create(
            shipment=shipment,
            stage_number=1,
            driver=shipment.courier,
            status="created",
            handover_required=shipment.requires_handover
        )


        return shipment
    

    def send_package_notification(self, package):
        Notification.objects.create(
            user=package.sender_user,  # recipient
            title="Your package has been assigned to a shipment",
            message=f"Package {package.package_id} is being prepared for delivery.",
            notification_type="shipment_update"
        )


class ShipmentStageSerializers(serializers.ModelSerializer):
    class Meta:
        model = ShipmentStage
        fields = "__all__"


class ShipmentReadSerializer(serializers.ModelSerializer):
    packages = PackageSerializer(many=True)
    stages = ShipmentStageSerializers(many=True)
    destinationoffice = serializers.SerializerMethodField()
    originoffice = serializers.SerializerMethodField()
    current_stage = serializers.SerializerMethodField()
    

    class Meta:
        model = Shipment
        fields = [
            "shipment_id","shipment_type", "packages", "origin_office", "originoffice", "destination_office", 
            "destinationoffice", "status", "courier", "stages", "current_stage",
        ]


    def get_originoffice(self, obj):
        return obj.origin_office.name
    
    def get_destinationoffice(self, obj):
        return obj.destination_office.name
    
    def get_current_stage(self, obj):
        return obj.current_stage
    


class ShipmentUpdateSerializer(serializers.ModelSerializer):
    driver_accepted = serializers.BooleanField()

    class Meta:
        model = Shipment
        fields = ["driver_accepted"]

    def update(self, instance, validated_data):
        driver_accepted = validated_data.get("driver_accepted")

        if driver_accepted:
            instance.status = "in_transit"
            instance.current_stage = 1
            instance.save(update_fields=["driver_accepted", "status", "current_stage"])

            # notify manager and package owners
            self.send_notifications(instance)
        return instance

    def send_notifications(self, shipment):
        # Notify manager
        if shipment.manager:
            Notification.objects.create(
                user=shipment.manager,
                title="Shipment accepted",
                message=f"Driver has accepted shipment {shipment.shipment_id}",
                shipment=shipment,
                notification_type="shipment_update"
            )

        # Notify all package owners
        for package in shipment.packages.all():
            Notification.objects.create(
                user=package.created_by,
                title="Package in Transit",
                message=f"Your package {package.package_id} is now in transit.",
                package=package,
                notification_type="shipment_update"
            )





