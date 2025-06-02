from rest_framework import serializers
from apps.accounts.models import User, Profile
from apps.logistics.models import *
from apps.accounts.serializers import UserSerializer

class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = "__all__"


class WareHouseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Warehouse
        fields = [
            "wid","name", "location", "county", "subcounty", "longitude", "latitude","email","phone","storage_type","total_storage",
            "available_storage", "loading_bays", "description", "status", "created_by", "created_at", "updated_at"
        ]


    


class OrderImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderImages
        fields = [
            "order", "image"
        ]


class OrderDetailsSerializer(serializers.ModelSerializer):
    createdBy = serializers.SerializerMethodField()
    orderPK = serializers.SerializerMethodField()
    orderID = serializers.SerializerMethodField()

    class Meta:
        model = OrderDetails
        fields = [
            'order_details_id', 'order', 'transaction_id', 'payment_method', 'pickup_confirmed', 'delivery_stage', 'delivery_status', 'updated_at', 'assigned_pickupto', "createdBy", "orderPK", "orderID"
        ]

    
    def get_createdBy(self, obj):
        return obj.order.created_by
    
    def get_orderPK(self, obj):
        return obj.order.id
    
    def get_orderID(self, obj):
        return obj.order.order_id
    



class OrderSerializer(serializers.ModelSerializer):
    images = OrderImagesSerializer(many=True, required=False)
    details = OrderDetailsSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "package_name", "delivery_type", "freight_type", "fragile", "urgency", "length", "width", "height", "weight",
            "sender_fullname", "sender_email", "sender_phone", "pickup_datetime", "pickup_location","pickup_latLng", "description","price",
            "recipient_fullname", "recipient_email", "recipient_phone", "recipient_location", "recipient_latLng", "order_id", 
            "order_number", "created_at", "updated_at", "details", "images", "created_by"
        ]


   



class ShipmentItemsSerializer(serializers.ModelSerializer):

    delivery_type = serializers.SerializerMethodField()
    freight_type = serializers.SerializerMethodField()
    fragile = serializers.SerializerMethodField()
    order_id = serializers.SerializerMethodField()
    sender_fullname = serializers.SerializerMethodField()
    sender_phone = serializers.SerializerMethodField()
    recipient_fullname = serializers.SerializerMethodField() 
    recipient_phone = serializers.SerializerMethodField()
    recipient_location = serializers.SerializerMethodField()

    class Meta:
        model = ShipmentItems
        fields = [
            "id", "order", "delivery_type", "freight_type", "fragile", "order_id", "sender_fullname", "sender_phone", "recipient_fullname", "recipient_phone", "recipient_location"
        ]

    def get_delivery_type(self, obj):
        return obj.order.delivery_type
    

    def get_freight_type(self, obj):
        return obj.order.freight_type

    def get_fragile(self, obj):
        return obj.order.fragile
    
    def get_order_id(self, obj):
        return obj.order.order_id
    
    def get_sender_fullname(self, obj):
        return obj.order.sender_fullname
    
    def get_sender_phone(self, obj):
        return obj.order.sender_phone

    def get_recipient_fullname(self, obj):
        return obj.order.recipient_fullname

    def get_recipient_phone(self, obj):
        return obj.order.recipient_phone
    
    def get_recipient_location(self, obj):
        return obj.order.recipient_location




class ShipmentLegSerializer(serializers.ModelSerializer):
    driverdata = serializers.SerializerMethodField()
    routename = serializers.SerializerMethodField()

    class Meta:
        model = ShipmentLeg
        fields = [
            "id", "shipment", "route", "routename", "driverdata", "status", "active"
        ]


    def get_routename(self, obj):
        return obj.route.name
    

    def get_driverdata(self, obj):
        try:
            user = User.objects.using("accounts").get(uid=obj.driver)
            return UserSerializer(user).data
        except User.DoesNotExist:
            return None




class ShipmentSerializer(serializers.ModelSerializer):
    items = ShipmentItemsSerializer(many=True, required=False)
    legs = ShipmentLegSerializer(many=True, required=False)
    routename = serializers.SerializerMethodField()

    class Meta:
        model = Shipment
        fields = [
            "id", "shipment_number", "created_at", "updated_at", "created_by", "assigned_to", "barcode_svg", 
            "delivery_stage", "delivery_status", "is_completed", "total_shipment_stages", "completed_shipment_stages", 
            "shipment_route", "shipment_type", "routename", "items", "legs", "partner_sharing", "partner"
        ]


    def get_routename(self, obj):
        return obj.shipment_route.name








