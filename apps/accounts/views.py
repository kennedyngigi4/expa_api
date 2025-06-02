from django.shortcuts import render, get_object_or_404
from rest_framework import status, generics, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from apps.accounts.models import User
from apps.accounts.serializers import RegistrationSerializer, LoginSerializer, UserSerializer

# Create your views here.
class RegistrationView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    queryset = User.objects.all()
    


    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                return Response({ "success": True, "message": "Account created!", "uid": user.uid })
            return Response({ "success": False, "message": user.errors })
        return Response({ "success": False, "message": "Failed to create account" })






class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer







class AllEmployeesView(generics.ListAPIView):
    permission_classes = [ IsAuthenticated ]
    serializer_class = UserSerializer
    queryset = User.objects.filter(role="Agent").order_by("-date_joined")



class AllDriversView(generics.ListAPIView):
    permission_classes = [ IsAuthenticated ]
    serializer_class = UserSerializer
    queryset = User.objects.filter(role="Driver").order_by("-date_joined")



class AllClients(generics.ListAPIView):
    permission_classes = [ IsAuthenticated ]
    serializer_class = UserSerializer
    queryset = User.objects.filter(role="Client").order_by("-date_joined")




class UserDetails(generics.RetrieveUpdateAPIView):
    permission_classes = [ IsAuthenticated ]
    serializer_class = UserSerializer
    queryset = User.objects.all()




class UserProfileView(APIView):
    permission_classes = [ IsAuthenticated ]
    

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
