from django.shortcuts import render

from firebase_admin import messaging

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from apps.accounts.permissions import *
from apps.messaging.models import *
from apps.messaging.serializers import *
from apps.drivers.models import *
from apps.messaging.firebase import *
# Create your views here.



class ClientNotificationsView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all().order_by("-created_at")
    permission_classes = [ IsAuthenticated, IsClient ]

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

    # ✅ new API in firebase-admin >= 6.x
    response = messaging.send_each_for_multicast(message)

    print("Sent:", response.success_count, "Failed:", response.failure_count)
    for idx, resp in enumerate(response.responses):
        if not resp.success:
            print(f"❌ Error for token {tokens[idx]}: {resp.exception}")

