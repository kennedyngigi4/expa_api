from django.shortcuts import render, get_object_or_404

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from apps.accounts.models import *
from apps.accounts.permissions import IsAdmin
from apps.payments.models import *
from apps.payments.serializers import *


class AllPaymentsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all().order_by("-date_created")


