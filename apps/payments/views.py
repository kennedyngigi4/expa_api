from django.shortcuts import render

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from apps.payments.models import *
from apps.payments.serializers import *
# Create your views here.


class InvoicesView(generics.ListAPIView):
    serializer_class = InvoiceSerializer
    queryset = Invoice.objects.all().order_by("-issued_at")
    permission_classes = [ IsAuthenticated ]


    def get_queryset(self):
        user = self.request.user
        queryset = Invoice.objects.filter(user=user)
        return queryset


