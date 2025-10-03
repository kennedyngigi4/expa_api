from django.shortcuts import render
from django.db.models import Q

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import *

from apps.accounts.models import *
from apps.accounts.serializers import *
from apps.accounts.permissions import *
from core.utils.emails import send_welcome_email
# Create your views here.


class RegistrationView(APIView):

    def post(self, request):
       
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_welcome_email(user)
            return Response({ "success": True, "message": "Registration successful" }, status=status.HTTP_201_CREATED)
        return Response({ "success": False, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



class LoginView(APIView):

    def post(self, request):
        
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            return Response({ "success": True, "message": serializer.validated_data}, status=status.HTTP_200_OK)
        return Response({ "success": False, "message": serializer.errors }, status=status.HTTP_400_BAD_REQUEST)






class OfficeView(generics.ListAPIView):
    serializer_class = OfficeSerializer
    queryset = Office.objects.all().order_by("name")



class CouriersView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.all()


    def get_queryset(self):
        queryset = self.queryset.filter(Q(role="driver") | Q(role="partner_rider")).order_by("full_name")
        return queryset



class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user




