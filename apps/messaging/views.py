from django.shortcuts import render

from rest_framework import status, generics, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.messaging.models import *
from apps.messaging.serializers import *
# Create your views here.


def SendNotification(recipient, subject, message, tracking, sender):
    notification = Notification.objects.create(
        sent_to=recipient,
        subject=subject,
        message=message,
        tracking=tracking,
        sender=sender,
    )
    notification.save()



class UserNotifications(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all().order_by("-created_at")


    def get_queryset(self):
        notifications = Notification.objects.filter(sent_to=self.request.user.uid).order_by("-created_at")
        return notifications



