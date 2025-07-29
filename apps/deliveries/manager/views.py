from django.shortcuts import render, get_object_or_404

from rest_framework import generics, status
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from apps.accounts.models import *
from apps.accounts.permissions import *
from apps.deliveries.models import *
from apps.deliveries.serializers import *



class ManagerDashboardStatsView(APIView):
    permission_classes = [ IsManager, IsAuthenticated]

    def get(self, request):
        user = self.request.user

        if not hasattr(user, 'office'):
            return Response({ "success": False, "message": "Manager is not linked to any office."}, status=400)

        office = user.office

        packages = Package.objects.filter(origin_office=office)
        shipments = Shipment.objects.all()

        orders = packages.count()
        unassigned_orders = packages.filter(shipments=None).count()
        shipments_out = shipments.filter(origin_office=office).count()
        shipments_in = shipments.filter(destination_office=office).count()
        outgoing_shipments = Shipment.objects.filter(manager=user, origin_office=office).order_by("-assigned_at")
        recent_shipments = ShipmentReadSerializer(outgoing_shipments, many=True).data

        return Response({
            "orders": orders,
            "unassigned_orders": unassigned_orders,
            "shipments_out": shipments_out,
            "shipments_in": shipments_in,
            "recent_shipments": recent_shipments,
        })




class ManagerOriginPackagesView(ListAPIView):
    serializer_class = PackageSerializer
    permission_classes = [ IsManager ]

    def get_queryset(self):
        user = self.request.user
        category = self.request.query_params.get("category")

        if not user.office:
            return Package.objects.none()
        
        queryset = Package.objects.filter(origin_office=user.office).order_by("-created_at")

        if category == "unassigned":
            queryset = queryset.filter(shipments=None)
        elif category == "assigned":
            queryset = queryset.filter(shipments__isnull=False, status="assigned")
        elif category == "in_transit":
            queryset = queryset.filter(shipments__status="in_transit")
        elif category == "delivered":
            queryset = queryset.filter(status="delivered")
        elif category == "all":
            queryset = queryset

        return queryset.distinct()


class ManagerPackageDetailsView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PackageSerializer
    queryset = Package.objects.all()
    permission_classes = [IsAuthenticated, IsManager]



class ManagerCreateShipmentView(generics.ListCreateAPIView):
    serializer_class = ShipmentSerializer
    permission_classes = [IsAuthenticated, IsManager]
    queryset = Shipment.objects.all()


    def post(self, request, *args, **kwargs):
    
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValidationError as ve:
            return Response({"success": False, "errors": ve.detail}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print("🚨 Unexpected Error:", str(e))
            print("Incoming Data:", request.data)

            return Response({"success": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class ManagerListShipmentView(generics.ListCreateAPIView):
    serializer_class = ShipmentReadSerializer
    permission_classes = [IsAuthenticated, IsManager]
    queryset = Shipment.objects.all()

    def get_queryset(self):
        user = self.request.user
        category = self.request.query_params.get("category")

        if not user.office:
            return Shipment.objects.none()
        
        queryset = Shipment.objects.filter(manager=user, origin_office=user.office).order_by("-assigned_at")

        if category == "assigned":
            queryset = queryset.filter(status="created")
        elif category == "in_transit":
            queryset = queryset.filter(status="in_transit")
        elif category == "delivered":
            queryset = queryset.filter(status="delivered")
        elif category == "returned":
            queryset = queryset.filter(status="returned")
        elif category == "cancelled":
            queryset = queryset.filter(status="cancelled")

        elif category == "all":
            queryset = queryset

        return queryset





class ManagerIncomingShipmentsView(generics.ListAPIView):
    serializer_class = ShipmentReadSerializer
    permission_classes = [IsAuthenticated, IsManager]
    queryset = Shipment.objects.all()


    def get_queryset(self):
        user = self.request.user
        category = self.request.query_params.get("category")

        if not user.office:
            return Shipment.objects.none()
        
        queryset = self.queryset.filter(destination_office=user.office)
        if category == "assigned":
            queryset = queryset.filter(status="created")
        elif category == "in_transit":
            queryset = queryset.filter(status="in_transit")
        elif category == "delivered":
            queryset = queryset.filter(status="delivered")
        elif category == "returned":
            queryset = queryset.filter(status="returned")
        elif category == "cancelled":
            queryset = queryset.filter(status="cancelled")
        elif category == "all":
            queryset = queryset

        
        return queryset




class ManagerShipmentDetailsView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsManager]
    serializer_class = ShipmentReadSerializer
    queryset = Shipment.objects.all()
    





