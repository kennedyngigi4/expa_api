from django.shortcuts import render, get_object_or_404
from rest_framework import status, generics, viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.accounts.models import User, Profile, DriverLocation
from apps.accounts.serializers import *



class CreateEmployeeView(APIView):
    permission_classes = [ IsAuthenticated ]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            employee = serializer.save()
            employee.created_by = request.user
            employee.save()
            if employee:
                profile, created = Profile.objects.update_or_create(
                    user=employee,
                    defaults={
                        "category": request.data.get("category"),
                        "warehouse": request.data.get("office"),
                    }
                )
                
                return Response({ "success": True, "message": "Account created!", "uid": employee.uid })
            return Response({ "success": False, "message": serializer.errors })
        return Response({ "success": False, "message": "Failed to create account" })



class AdminUpdateUserProfileView(viewsets.ModelViewSet):
    permission_classes = [ IsAuthenticated ]
    serializer_class = UserSerializer
    queryset = User.objects.all().select_related("profiles")
    lookup_field = "uid"

    def get_queryset(self):
        return super().get_queryset()
