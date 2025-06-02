from django.shortcuts import render, get_object_or_404

from rest_framework import status, generics, viewsets
from rest_framework.views import View
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.logistics.models import *
from apps.logistics.courier.serializers import *
from apps.messaging.models import *
from apps.messaging.serializers import *


class AssignedPickupsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        legs = ShipmentLeg.objects.filter(driver=request.user.uid, shipment__shipment_type="Pickup")


        shipment_ids = legs.values_list("shipment_id", flat=True).distinct()

        pickups = Shipment.objects.filter(
            id__in=shipment_ids,
            shipment_type="Pickup",
        ).exclude(delivery_status="COMPLETED")

        serializer = CourierShipmentSerializer(pickups, many=True)
        return Response(serializer.data)



class AssignedDeliveriesView(APIView):
    permission_classes = [ IsAuthenticated ]

    def get(self, request):
        legs = ShipmentLeg.objects.filter(driver=request.user.uid, shipment__shipment_type="Delivery")
        shipment_ids = legs.values_list("shipment_id", flat=True).distinct()

        deliveries = Shipment.objects.filter(
            id__in=shipment_ids,
            shipment_type="Delivery",
        ).exclude(delivery_status="COMPLETED")
        serializer = CourierShipmentSerializer(deliveries, many=True)
        return Response(serializer.data)



class CourierNotificationsView(generics.ListAPIView):
    permission_classes = [ IsAuthenticated ]
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()

    def get_queryset(self):
        notifications = Notification.objects.filter(sent_to=self.request.user.uid).order_by("-created_at")
        return notifications


class PickupsView(generics.ListAPIView):
    permission_classes = [ IsAuthenticated ]
    serializer_class = PickupSerializer
    queryset = OrderDetails.objects.all()


    def get_queryset(self):
        print(self.request.user.uid)
        assigned_pickups = OrderDetails.objects.filter(assigned_pickupto=self.request.user.uid, delivery_status="ASSIGNED")
        return assigned_pickups



class DriverShipmentView(generics.ListAPIView):
    permission_classes = [ IsAuthenticated ]
    serializer_class = ShipmentSerializer

    
    def get_queryset(self):
        driver = self.request.user

        # get shipmentlegs
        shipment_ids = ShipmentLeg.objects.filter(driver=driver.uid).values_list("shipment", flat=True)
        return Shipment.objects.filter(id__in=shipment_ids).distinct()




class StartDeliveryView(APIView):
    permission_classes = [ IsAuthenticated ]
    def post(self, request):
        driver_id = request.user.uid
        shipment_id = request.data.get("shipment_id")
        newstatus = request.data.get("status")

        if not driver_id or not shipment_id:
            return Response({ "error": "Missing required fields"  }, status=400)
        
        try:
            #1. update shipment leg status
            leg = ShipmentLeg.objects.get(driver=driver_id, active=True, shipment=shipment_id)
            leg.status = newstatus
            leg.save()
            
            #2. update shipmen delivery_status
            shipment = leg.shipment
            shipment.delivery_status = newstatus
            shipment.save()

            #3. Update shipment items statuses
            shipment.items.update(status=newstatus)
            
            return Response({"detail": "Status updated."}, status=200)
        except Shipment.DoesNotExist:
            return Response({ "error": "Shipment not found"}, status=status.HTTP_404_NOT_FOUND)







class IncidentViewSet(viewsets.ViewSet):
    permission_classes = [ IsAuthenticated ]

    def post(self, request):
        serializer = CourierIncidentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(driver=request.user.uid)
            return Response({ "message": "Submitted successfully"}, status=status.HTTP_200_OK)
        return Response({ "message": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)


    def list(self, request):
        queryset = Incident.objects.all().order_by("-created_at")
        serializer = CourierIncidentSerializer(queryset, many=True)
        return Response(serializer.data)


    def destroy(self, request, pk=None):
        pass

