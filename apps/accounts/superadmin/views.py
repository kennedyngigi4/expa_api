from django.shortcuts import render, get_object_or_404
from django.db.models import Q

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import NotFound

from apps.accounts.models import *
from apps.accounts.serializers import *
from apps.accounts.permissions import *
from apps.deliveries.models import *
from apps.deliveries.serializers import *
from apps.payments.models import *
from apps.payments.serializers import *



class CompanyStatisticsView(APIView):
    permission_classes = [ IsAdmin ]
    def get(self, request):
        all_orders = Package.objects.all().count()
        employees = User.objects.all().exclude(role__in=["admin", "client"]).count()
        manifests = Shipment.objects.all().count()
        offices = Office.objects.all().count()
        routes = InterCountyRoute.objects.all().count()
        drivers = User.objects.filter(role__in=["driver", "partner_rider"]).count()

        data = {
            "waybills": all_orders,
            "employees": employees,
            "manifests": manifests,
            "offices": offices,
            "routes": routes,
            "drivers": drivers
        }

        return Response(data)


class OfficeView(generics.ListCreateAPIView):
    serializer_class = OfficeSerializer
    queryset = Office.objects.all().order_by("name")


class OfficeDetailsUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OfficeSerializer
    queryset = Office.objects.all()
    lookup_field = "pk"



class AllUsersView(generics.ListAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [ IsAuthenticated, IsAdmin]

    def get_queryset(self):
        user = self.request.user
        roles = self.request.query_params.getlist("role")

        if user.role != "admin":
            return User.objects.none()

        if roles:
            queryset = User.objects.filter(role__in=roles).exclude(Q(role=user.role))
        else:
            queryset = User.objects.exclude(role=user.role)

        return queryset



class UserDetailsView(APIView):
    permission_classes = [ IsAuthenticated, IsAdmin]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise NotFound("User not found")
        
        orders = Package.objects.filter(
            Q(created_by=user) | Q(sender_user=user)
        )
        invoices = Invoice.objects.filter(user=user)


        user_data = UserSerializer(user).data
        orders_data = PackageSerializer(orders, many=True, context={"request": request}).data
        invoices_data = InvoiceSerializer(invoices, many=True).data

        data = {
            "user": user_data,
            "orders": orders_data,
            "invoices": invoices_data
        }

        return Response(data)

