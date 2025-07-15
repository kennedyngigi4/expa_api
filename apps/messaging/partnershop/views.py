from django.shortcuts import render

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from apps.accounts.permissions import *
from apps.messaging.models import *
from apps.messaging.serializers import *
# Create your views here.



class NotificationsView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all().order_by("-created_at")
    permission_classes = [ IsAuthenticated, IsPartnerPickup ]

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset.filter(user=user)
        return queryset
