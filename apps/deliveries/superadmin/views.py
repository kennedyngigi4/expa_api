from django.shortcuts import render


from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import *

from apps.accounts.models import *
from apps.accounts.permissions import *
from apps.deliveries.models import *
from apps.deliveries.serializers import *


class AllPackagesView(generics.ListAPIView):
    serializer_class = PackageSerializer
    queryset = Package.objects.all().order_by("-created_at")
    permission_classes = [ IsAuthenticated, IsAdmin ]   


class AllShipmentsView(generics.ListAPIView):
    serializer_class = ShipmentSerializer
    queryset = Shipment.objects.all()
    permission_classes = [ IsAuthenticated, IsAdmin]


