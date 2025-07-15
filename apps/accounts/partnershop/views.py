from django.shortcuts import render, get_object_or_404

from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.models import *
from apps.accounts.permissions import *
from apps.deliveries.models import *
from apps.messaging.models import *
from apps.payments.models import *



class PartnerShopStatisticsView(APIView):
    permission_classes = [ IsAuthenticated ]

    def get(self, request):
        user = self.request.user
        packages_count = Package.objects.filter(created_by=user).count()
        invoices_count = Invoice.objects.filter(user=user).count()
        notifications_count = Notification.objects.filter(user=user).count()

        data = {
            "packages": packages_count,
            "invoices": invoices_count,
            "notifications": notifications_count
        }
        return Response(data)


