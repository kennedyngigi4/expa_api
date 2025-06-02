from rest_framework import serializers
from apps.logistics.models import *
from apps.accounts.models import *


class ManagerOrderDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDetails
        fields = "__all__"


class ManagerOrderSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    client = serializers.SerializerMethodField()
    orderdetails = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = "__all__"

    
    def get_status(self, obj):
        items = ShipmentItems.objects.filter(order=obj).order_by("-created_at")
        if not items.exists():
            return "Unassigned"
        
        shipment = items.first().shipment
        if shipment.shipment_type == "Pickup":
            return "Pickup"
        elif shipment.shipment_type == "Delivery" and shipment.is_completed:
            return "Completed"
        elif shipment.shipment_type == "Delivery":
            return "Assigned"
        
        return "unknown"
        

    def get_client(self, obj):
        try:
            user = User.objects.using("accounts").get(uid=obj.created_by)
            profile = Profile.objects.using("accounts").get(user=user)

            
            return {
                "uid": str(user.uid),
                "fullname": user.fullname,
                "role": user.role,
                "account_type": profile.account_type,
            }
            
        except (User.DoesNotExist, Profile.DoesNotExist):
            return None


    def get_orderdetails(self, obj):
        try:
            orderdetails = OrderDetails.objects.get(order=obj)
            return ManagerOrderDetailsSerializer(orderdetails).data
        except OrderDetails.DoesNotExist:
            return None




class IncidentSerializer(serializers.ModelSerializer):
    shipmentNumber = serializers.SerializerMethodField()

    class Meta:
        model = Incident
        fields = "__all__"


    def get_shipmentNumber(self, obj):
        return obj.shipmen.shipment_number

