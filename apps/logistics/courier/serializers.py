from rest_framework import serializers
from apps.logistics.models import *



class CourierOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id", "package_name", "delivery_type", "freight_type", "fragile", "length", "width", "height",
            "weight", "sender_fullname", "sender_email", "sender_phone", "pickup_datetime", "pickup_location",
            "pickup_latLng", "description", "recipient_fullname", "recipient_email", "recipient_phone", "recipient_location",
            "recipient_latLng", "order_id"
        ]


class CourierShipmentItemSerializer(serializers.ModelSerializer):
    order = CourierOrderSerializer()

    class Meta:
        model = ShipmentItems
        fields = [
            "id", "order", "status"
        ]


class CourierShipmentSerializer(serializers.ModelSerializer):
    items = CourierShipmentItemSerializer(many=True)
    routename = serializers.SerializerMethodField()

    class Meta:
        model = Shipment
        fields = [
            "id", "shipment_number", "shipment_type", "shipment_route", "is_completed", "delivery_status",
            "delivery_stage", "assigned_to", "partner_sharing", "partner", "items", "created_by", "routename"
        ]

    def get_routename(self, obj):
        return obj.shipment_route.name




class CourierIncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incident
        fields = [
            "id", "shipment", "driver", "message"
        ]




class PickupSerializer(serializers.ModelSerializer):
    orderid = serializers.SerializerMethodField()
    sendername = serializers.SerializerMethodField()
    senderphone = serializers.SerializerMethodField()
    pickuplocation = serializers.SerializerMethodField()
    pickuplatLng = serializers.SerializerMethodField()
    recipientname = serializers.SerializerMethodField()
    recipientphone = serializers.SerializerMethodField()
    freighttype = serializers.SerializerMethodField()
    fragile = serializers.SerializerMethodField()
    length = serializers.SerializerMethodField()
    width = serializers.SerializerMethodField()
    height = serializers.SerializerMethodField()
    weight = serializers.SerializerMethodField()


    class Meta:
        model = OrderDetails
        fields = [
            "order_details_id", "order", "transaction_id", "pickup_confirmed", "assigned_pickupto", "delivery_stage", 
            "delivery_status", "orderid", "sendername", "senderphone", "recipientname", "recipientphone", "pickuplocation", "pickuplatLng",
            "freighttype", "fragile", "length", "width", "height", "weight"
        ]


    def get_orderid(self, obj):
        return obj.order.order_id


    def get_sendername(self, obj):
        return obj.order.sender_fullname
    
    def get_senderphone(self, obj):
        return obj.order.sender_phone
    

    def get_recipientname(self, obj):
        return obj.order.recipient_fullname


    def get_recipientphone(self, obj):
        return obj.order.recipient_phone
    

    def get_pickuplocation(self, obj):
        return obj.order.pickup_location
    
    def get_pickuplatLng(self, obj):
        return obj.order.pickup_latLng


    def get_freighttype(self, obj):
        return obj.order.freight_type

    def get_fragile(self, obj):
        return obj.order.fragile
    

    def get_length(self, obj):
        return obj.order.length
    
    def get_width(self, obj):
        return obj.order.width
    
    def get_height(self, obj):
        return obj.order.height
    
    def get_weight(self, obj):
        return obj.order.weight




class ShipmentLegSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipmentLeg
        fields = "__all__"


class ShipmentItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipmentItems
        fields = [
            "order", "shipment", "status", "assigned_at"
        ]


class ShipmentSerializer(serializers.ModelSerializer):
    items = ShipmentItemSerializer(many=True, read_only=True)
    legs = serializers.SerializerMethodField()

    class Meta:
        model = Shipment
        fields = [
            "id","shipment_number","delivery_stage","delivery_status", "is_completed", "total_shipment_stages", 
            "completed_shipment_stages", "items", "legs",
        ]

    
    def get_legs(self, obj):
        driver_id = str(self.context["request"].user.uid)
        legs = obj.legs.filter(driver=driver_id)
        return ShipmentLegSerializer(legs, many=True).data




