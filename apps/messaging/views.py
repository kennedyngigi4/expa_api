import requests 
import urllib 
import json
from firebase_admin import messaging

from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from apps.accounts.permissions import *
from apps.messaging.models import *
from apps.messaging.serializers import *
from apps.drivers.models import *
from apps.messaging.firebase import *
# Create your views here.



class NotificationsView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all().order_by("-created_at")
    permission_classes = [ IsAuthenticated ]

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset.filter(user=user)
        return queryset
    


def intracity_drivers_notification(drivers, title, body, data=None):
    init_firebase()
    tokens = list(
        DriverDevice.objects.filter(user__in=drivers)
        .exclude(fcm_token__isnull=True)
        .exclude(fcm_token__exact="")
        .values_list("fcm_token", flat=True)
    )

    if not tokens:
        print("No tokens found.")
        return


    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        tokens=tokens,
        data={str(k): str(v) for k, v in (data or {}).items()},
    )

    
    response = messaging.send_each_for_multicast(message)

    
    for idx, resp in enumerate(response.responses):
        if not resp.success:
            print(f"❌ Error for token {tokens[idx]}: {resp.exception}")






class SendSMSView(APIView):
    def post(self, request):
        url = "https://api.onfonmedia.co.ke/v1/sms/SendBulkSMS"
        payload = {
            "SenderId": "ExPa Parcel",
            "MessageParameters": [
                {"Number": "254701220024", "Text": "Test Message"},
            ],
            "ApiKey": " YlHirwKFLIDNbmaMZs8xQnv1p6o7qSXhVAgW3T2yG05kd94U",
            "ClientId": " expaparcel"
        }

        headers = {
            "Content-Type": "application/json",
            "AccessKey": "YlHirwKFLIDNbmaMZs8xQnv1p6o7qSXhVAgW3T2yG05kd94U",
        }

        try:
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            # response = requests.post(url, data=payload, headers=headers)
            response_data = response.json()
            return Response(response_data, status=response.status_code)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)












