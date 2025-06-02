from django.shortcuts import render, get_object_or_404
from django.utils.timezone import now, timedelta
from django.db.models import Count
from django.db.models.functions import TruncDate
from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import *
from rest_framework.views import APIView


from apps.accounts.models import *
from apps.accounts.permissions import *
from apps.logistics.models import *
from apps.logistics.serializers import *

# Create your views here.



class RouteView(viewsets.ViewSet):
    def list(self, request):
        queryset = Route.objects.all()
        serializer = RouteSerializer(queryset, many=True)
        return Response(serializer.data) 


    def create(self, request):
        serializer = RouteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user.uid)
            return Response({ "success": True, "message": "Route created" })
        return Response({ "success": False, "message": serializer.error_messages })

    def destroy(self, request, pk=None):
        queryset = Route.objects.all()
        route = get_object_or_404(queryset, id=pk)
        if route:
            route.delete()
            return Response({ "success": True, "message": "Deleted successfully" })
        return Response({ "success": False, "message": "An error occured, try again."})


class StatisticsView(APIView):
    def get(self, request):
        end_date = now().date()
        start_date = end_date - timedelta(days=13)
        
        # aggregate orders by day
        orders_by_day = (
            Order.objects
            .filter(created_at__date__range=(start_date, end_date))
            .annotate(date=TruncDate("created_at"))
            .values("date")
            .annotate(order_count=Count("id"))
            .order_by("date")
        )


        deliveries_by_day = (
            Shipment.objects
            .filter(created_at__date__range=(start_date, end_date))
            .annotate(date=TruncDate("created_at"))
            .values("date")
            .annotate(deliveries_count=Count("id"))
            .order_by("date")
        )

        

        date_counts = {item["date"]: item["order_count"]  for item in orders_by_day}
        deliveries_counts = { item["date"]: item["deliveries_count"] for item in deliveries_by_day}
        full_range = [start_date + timedelta(days=i) for i in range(14) ]
        result = [
            {"date": date, "orderscount": date_counts.get(date, 0), "deliveriescounts": deliveries_counts.get(date, 0) } for date in full_range
        ]

        total_customers = User.objects.filter(role="Client").count()
        total_drivers = User.objects.filter(role="Driver").count()
        total_employees = User.objects.filter(role="Agent").count()
        total_orders = Order.objects.count()

        return Response({ "result": result, "total_customers": total_customers, "total_drivers": total_drivers, "total_employees": total_employees, "total_orders": total_orders })



class WarehouseViewset(viewsets.ViewSet):
    serializer_class = WareHouseSerializer
    queryset = Warehouse.objects.all()
    permission_classes = [IsAuthenticated, IsAdmin]

    def list(self, request):
        queryset = self.queryset.order_by("-created_at")
        serializer = WareHouseSerializer(queryset, many=True)
        return Response(serializer.data)


    def create(self, request):
        serializer = WareHouseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user.uid)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def retrieve(self, request, pk=None):
        warehouse = get_object_or_404(Warehouse, wid=pk)
        if warehouse:
            serializer = WareHouseSerializer(warehouse)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)


    def partial_update(self, request, pk=None):
        warehouse = get_object_or_404(Warehouse, wid=pk)
        if warehouse:
            serializer = WareHouseSerializer(warehouse, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)


    def destroy(self, request, pk=None):
        warehouse = get_object_or_404(Warehouse, wid=pk)
        if warehouse:
            warehouse.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)



class WarehouseEmployeesView(APIView):
    permission_classes = [ IsAuthenticated ]

    def get(self, request, pk=None):

        try:
            warehouse = Warehouse.objects.get(wid=pk)
        except Warehouse.DoesNotExist:
            return Response({ "message": "Warehouse not found" }, status=status.HTTP_404_NOT_FOUND)
        

        profiles = Profile.objects.using("accounts").filter(warehouse=pk).select_related("user")
        data = [
            {
                "uid": profile.user.uid,
                "fullname": profile.user.fullname,
                "phone": profile.user.phone,
                "email": profile.user.email,
                "category": profile.category,
                "warehouse": warehouse.name
            }
            for profile in profiles
        ]

        return Response(data)



class CourierShipmentListView(APIView):
    def get(self, request, driver_id):
        shipment_ids = ShipmentLeg.objects.filter(driver=driver_id).values_list("shipment_id", flat=True)
        shipments = Shipment.objects.filter(id__in=shipment_ids).prefetch_related("items__order")

        serializer = ShipmentSerializer(shipments, many=True)
        return Response(serializer.data)



class ClientOrdersListView(APIView):
    permission_classes = [ IsAuthenticated ]
    def get(self, request, client_id):
        orders = Order.objects.filter(created_by=client_id).order_by("-created_at")
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class OrdersView(generics.ListAPIView):
    permission_classes = [ IsAuthenticated ]
    serializer_class = OrderSerializer
    queryset = Order.objects.all()


class OrderDetailsView(generics.RetrieveUpdateAPIView):
    permission_classes = [ IsAuthenticated ]
    serializer_class = OrderSerializer
    queryset = Order.objects.all()


class AllDeliveriesView(generics.ListAPIView):
    permission_classes = [ IsAuthenticated ]
    serializer_class = ShipmentSerializer
    queryset = Shipment.objects.all().order_by("-created_at")



class DeliveryDetailsView(generics.RetrieveUpdateAPIView):
    permission_classes = [ IsAuthenticated ]
    serializer_class = ShipmentSerializer
    queryset = Shipment.objects.all()





