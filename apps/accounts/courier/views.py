from django.shortcuts import render, get_object_or_404

from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response


from apps.accounts.models import DriverLocation
from apps.accounts.serializers import DriverLocationSerializer



class CourierLocationStreamView(APIView):
    def post(self, request):
        pass








