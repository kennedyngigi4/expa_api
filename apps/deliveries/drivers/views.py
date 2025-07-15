from django.shortcuts import render


from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import *
from apps.accounts.permissions import *
from apps.deliveries.models import *
from apps.deliveries.serializers import *



class DriversAllShipments(APIView):
    permission_classes = [ IsAuthenticated, IsRider ]

    def post(self, request):
        user = self.request.user

        # immediate shipments
        immediate_shipments = Shipment.objects.filter(
            courier=user,
            status__in=["created", "in_transit"]
        ).distinct().order_by("-assigned_at")

        # upcoming shipments
        stage_qs = ShipmentStage.objects.filter(
            driver=user,
            status__in=["pending", "awaiting"],
        ).select_related('shipment')
        upcoming_shipments = [stage.shipment for stage in stage_qs]

        immediate_data = ShipmentReadSerializer(immediate_shipments, many=True).data
        upcoming_data = ShipmentReadSerializer(upcoming_shipments, many=True).data


        return Response({
            "immediate": immediate_data,
            "upcoming": upcoming_data
        })




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

