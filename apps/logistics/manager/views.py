from django.shortcuts import render, get_object_or_404

from rest_framework import status, generics, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.accounts.models import *
from apps.accounts.permissions import *
from apps.logistics.models import *
from apps.logistics.serializers import *
from apps.logistics.manager.serializers import *
from apps.payments.views import MPESA
from apps.payments.models import *
from apps.payments.serializers import *
from core.utils.invoicing import create_invoice
from core.utils.user_registration import *



class ManagerStatisticsView(APIView):
    permission_classes = [ IsAuthenticated ]

    def get(self, request):
        user = request.user

        try:
            profile = user.profiles 
            warehouse_id  = profile.warehouse
            warehouse = Warehouse.objects.using("logistics").get(wid=warehouse_id)
            warehouse_region = warehouse.county.lower().strip()
        except Warehouse.DoesNotExist:
            return Response({"detail": "No warehouse profile or region found."}, status=400)
        except Exception as e:
            return Response({ "detail": str(e)}, status=400)


        unassigned_orders_count = Order.objects.filter(pickup_location__icontains=warehouse_region).count()
        orders_count = Order.objects.filter(created_by=user.uid).count()
        invoices_count = Invoice.objects.filter(created_by=user.uid).count()
        shipments_count = Shipment.objects.filter(created_by=user.uid).count()
        return Response({ "unassigned_orders_count": unassigned_orders_count, "orders_count": orders_count, "invoices_count": invoices_count, "shipments_count": shipments_count }) 


class LatestManagerRegionOrdersView(APIView):
    permission_classes = [ IsAuthenticated ]

    def get(self, request):
        user = request.user

        try:
            profile = user.profiles 
            warehouse_id  = profile.warehouse
            warehouse = Warehouse.objects.using("logistics").get(wid=warehouse_id)
            warehouse_region = warehouse.county.lower().strip()
        except Warehouse.DoesNotExist:
            return Response({"detail": "No warehouse profile or region found."}, status=400)
        except Exception as e:
            return Response({ "detail": str(e)}, status=400)
        
        orders = Order.objects.filter(pickup_location__icontains=warehouse_region).order_by("-created_at")
        serializer = ManagerOrderSerializer(orders, many=True)


        filtered_data = [ order for order in serializer.data if order.get("status") == "Unassigned" ]
        return Response(filtered_data)


class ManagerCreateOrder(APIView):
    permission_classes = [ IsAuthenticated ]

    def post(self, request):
        print(request.data)
        new_user = create_user(request.data["sender_email"], request.data["sender_phone"], request.data["sender_fullname"], request.user.uid)
        if new_user is not None:
            serializer = OrderSerializer(data=request.data)

            print("Before .....")
            if not serializer.is_valid():
                print("testing ...")
                return Response(serializer.errors, status=400)
                
            print("UID", request.user.uid)
            print("After .....")
            order = serializer.save(created_by=request.user.uid)
            print("order")
            if order:
                # 1. Generate an unpaid invoice
                create_invoice(new_user.uid, [order], created_by=request.user.uid)

                # 2. Initiate mpesa payments
                MPESA(request.data["sender_phone"], request.data["price"]).MpesaSTKPush()

                return Response({
                    "success": True,
                    "id": order.id,
                }, status=status.HTTP_201_CREATED)





class ClassifiedOrdersListView(APIView):
    permission_classes = [ IsAuthenticated ]



    def get(self, request):
        user = request.user

        try:
            profile = user.profiles 
            warehouse_id  = profile.warehouse
            warehouse = Warehouse.objects.using("logistics").get(wid=warehouse_id)
            warehouse_region = warehouse.county.lower().strip()
        except Warehouse.DoesNotExist:
            return Response({"detail": "No warehouse profile or region found."}, status=400)
        except Exception as e:
            return Response({ "detail": str(e)}, status=400)


        status_filter = request.query_params.get("status", None)
        orders = Order.objects.filter(pickup_location__icontains=warehouse_region).order_by("-created_at")
        serializer = ManagerOrderSerializer(orders, many=True)
        data = serializer.data

        if status_filter:
            data = [  order for order in data if order["status"] == status_filter ]

        return Response(data)


class UnassignedOrdersView(generics.ListAPIView):
    permission_classes = [ IsAuthenticated ]
    serializer_class = OrderSerializer
    queryset = Order.objects.all().order_by("-created_at")

    def get_queryset(self):
        assigned_orders_id = ShipmentItems.objects.values_list("order", flat=True)
        return Order.objects.exclude(id__in=assigned_orders_id)


class OrderDetailsView(generics.RetrieveUpdateAPIView):
    permission_classes = [ IsAuthenticated ]
    serializer_class = ManagerOrderSerializer
    queryset = Order.objects.all().order_by("-created_at")



class UpdateOrderView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [ IsAuthenticated ]
    serializer_class = OrderSerializer
    queryset = Order.objects.all()


class OrderDetailsUpdateView(generics.RetrieveUpdateAPIView):
    permission_classes = [ IsAuthenticated ]
    serializer_class = OrderDetailsSerializer
    queryset = OrderDetails.objects.all()



class ManagerInvoicesView(APIView):
    permission_classes = [ IsAuthenticated ]

    def get(self, request):
        invoices = Invoice.objects.filter(created_by=request.user.uid).order_by("-created_at")
        serializer = InvoiceSerializer(invoices, many=True)
        return Response(serializer.data)


class ShipmentsViewSet(viewsets.ViewSet):
    permission_classes = [ IsAuthenticated ]

    def create(self, request, *args, **kwargs):
        serializer = ShipmentSerializer(data=request.data)

        if serializer.is_valid():
            shipment = serializer.save(created_by=request.user.uid, delivery_status="PROCESSING")

            orders = request.data["selected_orders"]
            for order in orders:
                orderint = Order.objects.get(id=order["id"])
                ShipmentItems.objects.create(shipment=shipment, order=orderint, status="PROCESSING")



            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def list(self, request):
        queryset = Shipment.objects.filter(created_by=request.user.uid).order_by("-created_at")
        serializer = ShipmentSerializer(queryset, many=True)
        return Response(serializer.data)
    

    def retrieve(self, request, pk=None):
        queryset = Shipment.objects.filter(created_by=request.user.uid)
        shipment = get_object_or_404(queryset, id=pk)
        serializer = ShipmentSerializer(shipment)
        return Response(serializer.data)
    

    def destroy(self, request, pk=None):
        queryset = Shipment.objects.filter(created_by=request.user.uid)
        shipment = get_object_or_404(queryset, id=pk)
        if shipment:
            shipment.delete()
            return Response({ "success": True, "message": "Deleted successfully"})
        return Response({ "success": False, "message": "An error occured, try again."})



class CreatePickupShipmentView(generics.CreateAPIView):
    permission_classes = [ IsAuthenticated ]
    serializer_class = ShipmentSerializer
    queryset = Shipment.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = ShipmentSerializer(data=request.data)
        if serializer.is_valid():
            shipment = serializer.save(created_by=request.user.uid)
            if shipment:
                leg_serializer = ShipmentLegSerializer(data=request.data)
                if leg_serializer.is_valid():
                    route = Route.objects.get(id=request.data["shipment_route"])
                    leg_serializer.save(shipment=shipment, driver=request.data["driver"], created_by=request.user.uid, route=route, active=True)

                    # Add the selected order to Shipment Items
                    order = Order.objects.get(id=request.data["order"])
                    item = ShipmentItems.objects.create(shipment=shipment, order=order)
                    item.save()

                
                    
                
                return Response({ "success": True, "message": "Created successfully"})
            return Response({ "success": False, "message": "An error occured, try again."})
       
            
           



class ShipmentItemDeleteView(generics.DestroyAPIView):
    permission_classes = [ IsAuthenticated ]
    serializer_class = ShipmentItemsSerializer
    queryset = ShipmentItems.objects.all()

    def destroy(self, request, *args, **kwargs):
        queryset = ShipmentItems.objects.all()
        item = get_object_or_404(queryset, id=self.kwargs["pk"])
        if item:
            item.delete()
            return Response({ "success": True, "message": "Removed successfully"})
        return Response({ "success": False, "message": "An error occured, try again."})




class ShipmentLegView(generics.ListCreateAPIView):
    permission_classes = [ IsAuthenticated ]
    serializer_class = ShipmentLegSerializer
    queryset = ShipmentLeg.objects.all()

    def post(self, request, *args, **kwargs):
        new_shipment=Shipment.objects.get(id=request.data["shipment"])
        selected_route = Route.objects.get(id=request.data["route"])
        shipmentleg = ShipmentLeg.objects.create(
            driver=request.data["driver"],
            route=selected_route,
            shipment=new_shipment,
            active=request.data["active"]
        )
        data = shipmentleg.save()
        
        return Response({ "success": True })



class DeleteShipmentLegView(generics.DestroyAPIView):
    permission_classes = [ IsAuthenticated ]
    serializer_class = ShipmentLegSerializer
    queryset = ShipmentLeg.objects.all()

    def destroy(self, request, *args, **kwargs):
        queryset = ShipmentLeg.objects.all()
        leg = get_object_or_404(queryset, id=self.kwargs["pk"])
        if leg:
            leg.delete()
            return Response({ "success": True, "message": "Removed successfully"})
        return Response({ "success": False, "message": "An error occured, try again."})





class ManagerShipmentIncidentsView(APIView):
    permission_classes = [ IsAuthenticated ]

    def get(self, request):
        uid = str(request.user.uid)

        # Get Manager shipments
        manager_shipments = Shipment.objects.filter(created_by=uid)
        incidents = Incident.objects.filter(shipment__in=manager_shipments)

        serializer = IncidentSerializer(incidents, many=True)
        return Response(serializer.data)




