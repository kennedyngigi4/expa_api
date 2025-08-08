from django.shortcuts import render


from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import *
from apps.accounts.permissions import *
from apps.deliveries.models import *
from apps.deliveries.serializers import *
from apps.deliveries.drivers.serializers import *

from apps.messaging.models import Notification
from apps.messaging.utils import *
from apps.messaging.serializers import *


class DriverAssignedShipmentsView(generics.ListAPIView):
    serializer_class = RiderShipmentSerializer
    permission_classes = [ IsAuthenticated, IsRider ]

    def get_queryset(self):
        user = self.request.user
        data = Shipment.objects.filter(
            stages__driver=user
        ).distinct().prefetch_related(
            'shipmentpackage_set__package',
            'stages',
        ).select_related('origin_office', 'destination_office').exclude(status="DELIVERED")
        
        return data


class DriverCompletedShipmentsView(generics.ListAPIView):
    serializer_class = RiderShipmentSerializer
    permission_classes = [ IsAuthenticated, IsRider ]

    def get_queryset(self):
        user = self.request.user
        data = Shipment.objects.filter(
            stages__driver=user,
            status="DELIVERED"
        ).distinct().prefetch_related(
            'shipmentpackage_set__package',
            'stages',
        ).select_related('origin_office', 'destination_office')
        
        return data


class DriverShipmentDetailView(generics.RetrieveUpdateAPIView):
    queryset = Shipment.objects.all()
    permission_classes = [IsAuthenticated, IsRider] 

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ShipmentUpdateSerializer
        return ShipmentReadSerializer


    def get_object(self):
        shipment = super().get_object()

        if shipment.courier != self.request.user:
            raise PermissionDenied("You are not assigned to this shipment.")

        return shipment

    def patch(self, request, *args, **kwargs):
        try:
            return super().patch(request, *args, **kwargs)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)




class UpdateShipmentStatusView(APIView):
    permission_classes = [ IsRider, IsAuthenticated ]


    def post(self, request, shipment_id):
        user = self.request.user
        new_status = request.data.get("status")

        try:
            shipment = Shipment.objects.get(shipment_id=shipment_id)

            # check driver/rider is the assigned one
            if not shipment.stages.filter(driver=user).exists():
                return Response({ "success": False, "message": "You’re not assigned to this shipment."}, status=status.HTTP_403_FORBIDDEN)
            
            # update shipment status
            shipment.status = new_status
            shipment.save()

            # update package status and notify users
            shipment_packages = ShipmentPackage.objects.filter(shipment=shipment).select_related("package")


            for item in shipment_packages:
                package = item.package
                print(new_status)
                # update package status
                if new_status == "IN_TRANSIT":
                    item.status = PackageStatus.IN_TRANSIT
                    package.status = PackageStatus.IN_TRANSIT

                elif new_status == "DELIVERED":
                    item.status = PackageStatus.DELIVERED
                    item.delivered = True
                    package.status = PackageStatus.DELIVERED
                    
                elif new_status == "HANDOVER":
                    item.status = PackageStatus.HANDOVER
                    package.status = PackageStatus.HANDOVER
                package.save()
                item.save()


                # send notification to sender & recipient
                sender = item.package.created_by
                if sender:
                    sender_notification = send_notification(
                        user=sender,
                        title=f"Package {item.package.package_id} update",
                        message=f"Your package is now {item.status}.",
                    )

                    # TO-DO: send messages and emails to recipient 

            return Response({"success": True, "message": "Shipment and packages updated."}, status=200)
        except Shipment.DoesNotExist:
            return Response({ "success": False, "message": "Shipment not found."}, status=404)





class DriverNotificationsView(generics.ListAPIView):
    permission_classes = [ IsRider, IsAuthenticated ]
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all().order_by("-created_at")


    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset.filter(user=user)
        return queryset

