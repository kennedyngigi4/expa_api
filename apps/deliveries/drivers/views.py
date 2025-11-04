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
        ).select_related('origin_office', 'destination_office').exclude(status="delivered")
        
        return data


class DriverCompletedShipmentsView(generics.ListAPIView):
    serializer_class = RiderShipmentSerializer
    permission_classes = [ IsAuthenticated, IsRider ]

    def get_queryset(self):
        user = self.request.user
        data = Shipment.objects.filter(
            stages__driver=user,
            status="delivered"
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

                # === STATUS HANDLING ===
                if new_status == "in_transit":
                    item.status = PackageStatus.in_transit
                    package.status = PackageStatus.in_transit

                elif new_status == "delivered":
                    
                    if shipment.shipment_type in ["pickup", "transfer"]:
                        item.status = PackageStatus.in_office
                        package.status = PackageStatus.in_office

                        
                        if shipment.destination_office:
                            package.current_office = shipment.destination_office
                    else:
                       
                        item.status = PackageStatus.delivered
                        package.status = PackageStatus.delivered

                    item.delivered = True

                elif new_status == "handover":
                    item.status = PackageStatus.handover
                    package.status = PackageStatus.handover

                package.save()
                item.save()


                # send notification to sender & recipient
                sender = package.created_by
                if sender:
                    send_notification(
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







class ProofofDeliveryView(APIView):
    permission_classes = [ IsAuthenticated ]

    def post(self, request, id):
       
        try:
            shipment = Shipment.objects.get(shipment_id=id)
            print(shipment)
        except Shipment.DoesNotExist:
            return Response({ "success": False, "message": "Shipment not found."}, status=status.HTTP_404_NOT_FOUND)
        

        serializer = ProofOfDeliverySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(shipment=shipment, uploaded_by=self.request.user)
            return Response({ "success": True, "message": "Upload successful."}, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response({ "success": False, "message": serializer.errors }, status=status.HTTP_400_BAD_REQUEST)
    
    
    def get(self, request, id):
        """Fetch all proofs of a shipment"""
        proofs = ProofOfDelivery.objects.filter(shipment=id)
        serializer = ProofOfDeliverySerializer(proofs, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
