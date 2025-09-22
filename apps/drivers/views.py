from django.shortcuts import render, get_object_or_404
from geopy.distance import geodesic

from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import * 
from apps.accounts.permissions import *
from apps.drivers.models import *
from apps.drivers.serializers import *
from apps.accounts.models import User
from apps.drivers.services import *



class DriverStatistics(APIView):
    permission_classes = [ IsAuthenticated, IsRider ]

    def get(self, request, *args, **kwargs):
        courier = self.request.user

        completed = Shipment.objects.filter(
            courier=courier,
            status="completed"
        ).count()

        ongoing = Shipment.objects.filter(
            courier=courier,
        ).exclude(status="completed").count()

        return Response({
            "completed": completed,
            "ongoing": ongoing
        })



class RegisterFCMToken(APIView):
    def post(self, request, *args, **kwargs):
        token = request.data.get("token")
        user = self.request.user

        if token:
            DriverDevice.objects.update_or_create(
                user=user,
                defaults={"fcm_token": token}
            )
            return Response({"success": True})
        return Response({"error": "Token missing"}, status=status.HTTP_400_BAD_REQUEST)



class DriverLocationUpdate(generics.GenericAPIView):
    permission_classes = [ IsAuthenticated, IsRider ]
    serializer_class = DriverLocationSerializer

    def post(self, request, *args, **kwargs):
        
        location, created = DriverLocation.objects.update_or_create(
            driver=self.request.user,
            defaults={
                "latitude": request.data.get("latitude"),
                "longitude": request.data.get("longitude"),
            }
        )

        serializer = self.get_serializer(location)
        return Response(serializer.data)


def get_nearby_drivers(pickup_coords, radius_km=5):
    nearby_drivers = []

    for driver_location in DriverLocation.objects.select_related("driver"):
        driver_coords = (float(driver_location.latitude), float(driver_location.longitude))
        distance = geodesic(pickup_coords, driver_coords).km

        if distance <= radius_km:
            nearby_drivers.append(driver_location.driver)  # ✅ return driver instead of location

    return nearby_drivers




class GetOrderDetailsView(APIView):
    permission_classes = [IsAuthenticated, IsRider]

    def get(self, request, order_id, *args, **kwargs):
        package = get_object_or_404(Package, id=order_id)
        serializer = DriverOrderDetails(package)
        return Response(serializer.data, status=status.HTTP_200_OK)



class AcceptDeliveryView(APIView):
    permission_classes = [IsAuthenticated, IsRider]

    def post(self, request, *args, **kwargs):
        courier = self.request.user
        data = request.data

        package = get_object_or_404(Package, id=data["id"])

        # Check if package already in shipment
        existing_shipment = Shipment.objects.filter(
            packages=package,
            status__in=["created", "in_transit"]
        ).first()


        if existing_shipment:
            return Response({
                "success": False,
                "message": "This order is already assigned to another rider.",
            }, status=status.HTTP_400_BAD_REQUEST)


        # Get manager from package's origin office
        manager = None
        if package.origin_office:
            manager = User.objects.filter(
                role="manager",
                office=package.origin_office  # assuming User has office FK
            ).first()

        # Create shipment
        shipment = create_intracity_shipment(
            package, courier, manager=manager
        )

        return Response({
            "success": True,
            "message": "Shipment created successfully.",
            "shipment_id": shipment.id
        }, status=status.HTTP_201_CREATED)


class DriverCompletedShipmentsView(APIView):
    permission_classes = [IsAuthenticated, IsRider]
    def get(self, request, *args, **kwargs):
        driver = request.user
        shipments = Shipment.objects.filter(
            courier=driver,
            status="completed"
        ).order_by("-delivered_at")

        serializer = DriverShipmentSerializer(shipments, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class DriverIncompleteShipmentsView(APIView):
    permission_classes = [IsAuthenticated, IsRider]
    def get(self, request, *args, **kwargs):
        driver = request.user
        shipments = Shipment.objects.filter(
            courier=driver
        ).exclude(status="completed").order_by("-assigned_at")

        serializer = DriverShipmentSerializer(shipments, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)



class ShipmentDetailsUpdatesView(APIView):
    permission_classes = [IsAuthenticated, IsRider]


    def get(self, request, shipment_id, *args, **kwargs):
        courier = self.request.user

        shipment = get_object_or_404(Shipment, id=shipment_id, courier=courier)
        serializer = DriverShipmentSerializer(shipment, context={"request": request})
        return Response(serializer.data)





class ShipmentUpdateStatusView(APIView):
    permission_classes = [IsAuthenticated, IsRider]


    def post(self, request, shipment_id):
        action = request.data.get("action")

        try:
            shipment = Shipment.objects.get(
                id=shipment_id, courier=self.request.user
            )
        
        except Shipment.DoesNotExist:
            return Response({ "success": False, "message": "Shipment not found."}, status=status.HTTP_404_NOT_FOUND)
        

        if action == "in_transit":
            shipment.status = "in_transit"
        elif action == "completed":
            shipment.status = "completed"
        else:
            return Response({ "success": False, "message": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)
        

        shipment.save()
        serializer = DriverShipmentSerializer(shipment)
        return Response({
            "success": True,
            "message": "Update successful."
        }, status=status.HTTP_200_OK)
        


