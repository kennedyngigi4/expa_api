from django.shortcuts import render, get_object_or_404

from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.models import DriverLocation
from apps.accounts.serializers import DriverLocationSerializer



class CourierLocationStreamView(APIView):
    permission_classes = [ IsAuthenticated ]

    def post(self, request):
        serializer = DriverLocationSerializer(data=request.data)
        if serializer.is_valid():
            location, _ = DriverLocation.objects.update_or_create(
                driver=request.user,
                defaults = {
                    "latitude": serializer.validated_data["latitude"],
                    "longitude": serializer.validated_data["longitude"],
                }
            )

            return Response({ "message": "Location updated"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)        









