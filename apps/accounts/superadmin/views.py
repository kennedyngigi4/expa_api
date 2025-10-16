from django.shortcuts import render, get_object_or_404
from django.db.models import Q

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser


from apps.accounts.models import *
from apps.accounts.serializers import *
from apps.accounts.permissions import *



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


