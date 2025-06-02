from django.shortcuts import render, get_object_or_404

from rest_framework import status, generics, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.logistics.models import *
from apps.accounts.models import *
from apps.logistics.serializers import *
from apps.payments.views import *
from apps.payments.models import *
from core.utils.invoicing import *

from apps.payments.serializers import *


class AllRoutesView(generics.ListAPIView):
    serializer_class = RouteSerializer
    queryset = Route.objects.all().order_by("name")



class CreateOrderView(APIView):
    permission_classes = [ IsAuthenticated ]

    def post(self, request):
        user = request.user
        serializer = OrderSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        order = serializer.save(created_by=user.uid)
        images = request.FILES.getlist("images")
        saved_images = []
        for newimage in images:
            order_image = OrderImages.objects.create(order=order, image=newimage)
            saved_images.append(OrderImagesSerializer(order_image).data)

        if order:
            # 1. Generate an unpaid invoice
            create_invoice(user.uid, [order], created_by=user.uid)

            # 2. Initiate mpesa payments
            MPESA(request.data["sender_phone"], request.data["price"]).MpesaSTKPush()

        return Response({
            "success": True,
            "id": order.id,
        }, status=status.HTTP_201_CREATED)




class MyOrdersView(generics.ListAPIView):
    permission_classes = [ IsAuthenticated ]
    serializer_class = OrderSerializer
    queryset = Order.objects.all()


    def get_queryset(self):
        return Order.objects.filter(created_by=self.request.user.uid).order_by("-created_at")
         


class OrderDetailsView(APIView):
    def get(self, request, pk):
        order = get_object_or_404(Order.objects.prefetch_related("details"), pk=pk)
        serializer = OrderSerializer(order)
        return Response(serializer.data)



class UpdateDetailsView(generics.RetrieveUpdateAPIView):
    permission_classes = [ IsAuthenticated ]
    serializer_class = OrderDetailsSerializer
    queryset = OrderDetails.objects.all()

    # def partial_update(self, request, *args, **kwargs):
    #     print(request.data)









