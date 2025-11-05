import requests
from apps.messaging.models import Notification
from django.conf import settings

from rest_framework import status
from rest_framework.response import Response

def send_notification(user, title, message):
    if user:
        Notification.objects.create(
            user=user,
            title=title,
            message=message
        )




def send_message(phone, message):
    url = settings.ONFON_SMS_URL
    payload = {
        "SenderId": settings.ONFON_SENDERID,
        "MessageParameters": [
            {"Number": phone, "Text": message},
        ],
        "ApiKey": settings.ONFON_APIKEY,
        "ClientId": settings.ONFON_CLIENTID
    }

    headers = {
        "AccessKey": settings.ONFON_CLIENTID,
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()
        # return Response(response_data, status=response.status_code)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



