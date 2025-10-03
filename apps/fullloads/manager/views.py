from django.shortcuts import render, get_object_or_404

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import *
from apps.fullloads.models import *
from apps.fullloads.serializers import *



class AllOfficeFullloadsView(generics.ListAPIView):
    permission_classes = [ IsAuthenticated, IsManager ]
    serializer_class = BookingReadSerializer
    queryset = Booking.objects.all().order_by("-created_at")


    def get_queryset(self):
        manager = self.request.user
        queryset = self.queryset.filter(
            origin_office=manager.office
        )
        return queryset

