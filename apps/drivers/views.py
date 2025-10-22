from django.shortcuts import render, get_object_or_404
from geopy.distance import geodesic

from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import * 
from apps.accounts.permissions import *
from apps.drivers.models import *
from apps.drivers.serializers import *
from apps.accounts.models import User
from apps.drivers.services import *



class DriverStatistics(APIView):
    permission_classes = [ IsAuthenticated, IsRider ]

    def get(self, request, *args, **kwargs):
        courier = self.request.user

        completed = Shipment.objects.filter(
            courier=courier,
            status__in=["completed", "Completed", "Delivered", "delivered"]
        ).count()

        ongoing = Shipment.objects.filter(
            courier=courier,
        ).exclude(status__in=["completed", "Completed", "Delivered", "delivered"]).count()

        wallet = Wallet.objects.get(
            user=courier
        )

        return Response({
            "completed": completed,
            "ongoing": ongoing,
            "amount": wallet.balance
        })



class RegisterFCMToken(APIView):
    def post(self, request, *args, **kwargs):
        token = request.data.get("token")
        user = self.request.user

        if token:
            DriverDevice.objects.update_or_create(
                user=user,
                defaults={"fcm_token": token}
            )
            return Response({"success": True})
        return Response({"error": "Token missing"}, status=status.HTTP_400_BAD_REQUEST)



class DriverLocationUpdate(generics.GenericAPIView):
    permission_classes = [ IsAuthenticated, IsRider ]
    serializer_class = DriverLocationSerializer

    def post(self, request, *args, **kwargs):
        
        location, created = DriverLocation.objects.update_or_create(
            driver=self.request.user,
            defaults={
                "latitude": request.data.get("latitude"),
                "longitude": request.data.get("longitude"),
            }
        )

        serializer = self.get_serializer(location)
        return Response(serializer.data)







class GetOrderDetailsView(APIView):
    permission_classes = [IsAuthenticated, IsRider]

    def get(self, request, order_id, *args, **kwargs):
        
        package = get_object_or_404(Package, id=order_id)
        serializer = DriverOrderDetails(package)

        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)



class AcceptDeliveryView(APIView):
    permission_classes = [IsAuthenticated, IsRider]

    def post(self, request, *args, **kwargs):
        courier = self.request.user
        data = request.data

        package = get_object_or_404(Package, id=data["id"])

        # Check if package already in shipment
        existing_shipment = Shipment.objects.filter(
            packages=package,
            status__in=["created", "pending", "assigned", "in_transit"]
        ).first()


        if existing_shipment:
            return Response({
                "success": False,
                "message": "This order is already assigned to another rider.",
            }, status=status.HTTP_400_BAD_REQUEST)


        # Get manager from package's origin office
        manager = None
        if package.origin_office:
            manager = User.objects.filter(
                role="manager",
                office=package.origin_office 
            ).first()

        # Select shipment creation type
        if package.delivery_type == "intra_city":
            shipment = create_intracity_shipment(
                package, courier, manager=manager
            )
        
        elif package.delivery_type == "inter_county" and package.requires_pickup:
            shipment = create_inoffice_shipment(package, courier, manager)

        else:
            return Response({
                "success": False,
                "message": "This package type is not available for direct rider pickup."
            }, status=status.HTTP_400_BAD_REQUEST)

        package.status = "assigned"
        package.save()

        # ShipmentPackage update
        shipment_package, _ = ShipmentPackage.objects.get_or_create(
            shipment=shipment,package=package
        )
        shipment_package.status = "assigned"
        shipment_package.save()

        # shipment update
        shipment.status = "assigned"
        shipment.save()

        commission_rate = Decimal("0.20")
        driver_earnings = package.fees * commission_rate
        rider_wallet, _ = Wallet.objects.get_or_create(user=courier)

        WalletTransaction.objects.create(
            wallet =rider_wallet,
            shipment=shipment,
            amount=driver_earnings,
            transaction_type="credit",
            status="pending",
            note=f"Reserved earnings for {shipment.shipment_id}"
        )

        return Response({
            "success": True,
            "message": "Shipment created successfully.",
            "shipment_id": shipment.id
        }, status=status.HTTP_201_CREATED)


class DriverCompletedShipmentsView(APIView):
    permission_classes = [IsAuthenticated, IsRider]
    def get(self, request, *args, **kwargs):
        driver = request.user

        shipments = Shipment.objects.filter(
            courier=driver,
            status="delivered"
        ).order_by("-delivered_at")

        serializer = DriverShipmentSerializer(shipments, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class DriverIncompleteShipmentsView(APIView):
    permission_classes = [IsAuthenticated, IsRider]
    def get(self, request, *args, **kwargs):
        driver = request.user
        shipments = Shipment.objects.filter(
            courier=driver
        ).exclude(status="delivered").order_by("-assigned_at")

        serializer = DriverShipmentSerializer(shipments, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)



class ShipmentDetailsUpdatesView(APIView):
    permission_classes = [IsAuthenticated, IsRider]


    def get(self, request, shipment_id, *args, **kwargs):
        courier = self.request.user

        shipment = get_object_or_404(Shipment, id=shipment_id, courier=courier)
        serializer = DriverShipmentSerializer(shipment, context={"request": request})

        print(serializer.data)
        return Response(serializer.data)





class ShipmentUpdateStatusView(APIView):
    permission_classes = [IsAuthenticated, IsRider]


    def post(self, request, shipment_id):
        courier = self.request.user
        action = request.data.get("action")

        try:
            shipment = Shipment.objects.get(
                id=shipment_id, courier=courier
            )
        
        except Shipment.DoesNotExist:
            return Response({ "success": False, "message": "Shipment not found."}, status=status.HTTP_404_NOT_FOUND)
        

        if action == "in_transit":
            shipment.status = "in_transit"
            shipment.save(update_fields=["status"])
            
            # stages 
            ShipmentStage.objects.filter(
                shipment=shipment, driver=courier, status__in=["created", "pending", "assigned"]
            ).update(status="in_transit")

            # ShipmentPackages
            ShipmentPackage.objects.filter(
                shipment=shipment
            ).update(status="in_transit")

            # Packages
            Package.objects.filter(
                shipments=shipment
            ).update(status="in_transit")

        # Delivered
        elif action == "delivered":
            shipment.status = "delivered"
            shipment.delivered_at = timezone.now()
            shipment.save(update_fields=["status", "delivered_at"])
            
            # stages 
            stage = (
                ShipmentStage.objects.filter(
                    shipment=shipment, driver=courier
                ).order_by("-stage_number").first()
            )

            
            if stage:
                stage.status = "delivered"
                stage.completed_at = timezone.now()
                stage.save(update_fields=["status", "completed_at"])

                destination_office = stage.to_office
            else:
                destination_office = shipment.destination_office


            if shipment.shipment_type in ["transfer", "pickup"]:
                final_status = PackageStatus.in_office
            else:
                final_status = PackageStatus.delivered

            # ShipmentPackages
            ShipmentPackage.objects.filter(
                shipment=shipment
            ).update(
                status=final_status
            )

            # Packages
            update_fields = { "status": final_status}
            if shipment.destination_office:
                update_fields["current_office"] = shipment.destination_office

            packages = Package.objects.filter(shipments=shipment)
            packages.update(**update_fields)

            transaction = WalletTransaction.objects.filter(
                wallet=courier.wallet,
                shipment=shipment,
                status="pending"
            ).first()

            if transaction:
                transaction.status = "completed"
                transaction.save(update_fields=["status"])
                courier.wallet.credit(transaction.amount)

            # Increment delivery counts
            wallet = courier.wallet
            wallet.completed_deliveries_since_withdrawal += 1
            wallet.save(update_fields=["completed_deliveries_since_withdrawal"])

        else:
            return Response({ "success": False, "message": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)
        

        shipment.save()
        serializer = DriverShipmentSerializer(shipment)
        return Response({
            "success": True,
            "message": "Update successful."
        }, status=status.HTTP_200_OK)
        


class WithdrawalWalletView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        rider = request.user
        wallet = getattr(rider, "wallet", None)

        if not wallet:
            return Response({
                "success": False,
                "message": "Wallet not found."
            }, status=status.HTTP_404_NOT_FOUND)

        
        if wallet.completed_deliveries_since_withdrawal < 10:
            return Response({
                "success": False,
                "message": f"You need at least 10 completed deliveries before withdrawing. "
                           f"Current: {wallet.completed_deliveries_since_withdrawal}"
            }, status=status.HTTP_400_BAD_REQUEST)

        
        try:
            amount = Decimal(request.data.get("amount", 0))
        except:
            amount = Decimal(0)

        if amount <= 0 or amount > wallet.balance:
            return Response({
                "success": False,
                "message": "Invalid withdrawal amount."
            }, status=status.HTTP_400_BAD_REQUEST)

        
        transaction = WalletTransaction.objects.create(
            wallet=wallet,
            amount=amount,
            transaction_type="debit",
            status="pending",  
            note="Withdrawal request to Nobuk"
        )

        
        wallet.balance -= amount
        wallet.completed_deliveries_since_withdrawal = 0
        wallet.save()

        # send to Nobuk here
        # send_withdrawal_request_to_nobuk.delay(transaction.id)

        return Response({
            "success": True,
            "message": "Withdrawal request submitted successfully. Awaiting Nobuk confirmation.",
            "transaction_id": transaction.id,
            "new_balance": str(wallet.balance)
        }, status=status.HTTP_201_CREATED)
        




class RiderWalletTransactionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rider = request.user
        wallet = getattr(rider, "wallet", None)

        if not wallet:
            return Response({
                "success": False,
                "message": "Wallet not found."
            }, status=404)

        transactions = wallet.transactions.all().order_by("-created_at")
        serializer = WalletTransactionSerializer(transactions, many=True)

        print(serializer.data)

        return Response({
            "success": True,
            "balance": str(wallet.balance),
            "transactions": serializer.data
        })


