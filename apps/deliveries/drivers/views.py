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
        ).select_related('origin_office', 'destination_office')
        print(data)
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

