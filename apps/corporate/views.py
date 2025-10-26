from django.shortcuts import render
from django.db.models import Q

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import IsOwnerOrAdmin
from apps.corporate.serializers import *
from apps.corporate.models import *
from core.utils.services import get_nearest_office


# Create your views here.
class CalculatePriceView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            weight = Decimal(data.get("weight", 0))
            recipient_latLng = data.get("recipient_latLng")

            destination_coords =  tuple(round(float(coord), 5) for coord in recipient_latLng.split(","))

            if not destination_coords:
                return Response({ "success": False, "message": "Destination coordinates required."}, status=status.HTTP_400_BAD_REQUEST)

            destination_office = get_nearest_office(destination_coords)

            if not destination_office:
                return Response({ "success": False, "message": "No nearby office found"}, status=status.HTTP_404_NOT_FOUND)

            

            # Origin office = corporate office of logged in user
            user = self.request.user
            if not hasattr(user, "corporate_office"):
                return Response({ "success": False, "message": "No corporate office linked"}, status=status.HTTP_400_BAD_REQUEST)

            origin_office = user.corporate_office
            
            try:
                route = CorporateRoute.objects.filter(origin_office=origin_office.id, destination_office=destination_office.id).first()
            except CorporateRoute.DoesNotExist:
                return Response({"success": False, "message": "No route found for offices"}, status=status.HTTP_404_NOT_FOUND)
            
            tiers = CorporateRoutePricing.objects.filter(route=route.id).order_by("min_weight")
            
            price = None
            for tier in tiers:
                if tier.min_weight <= weight <= tier.max_weight:
                    if tier.price:
                        price = weight * tier.price
                    else:
                        price = tier.price
                    break

            if price is None:
                return Response({ "success": False, "message": "No pricing tier matched"}, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                "price": round(price, 2),
                "origin_office": origin_office.name,
                "destination_office": destination_office.name,
            })

        except Exception as e:
            return Response({ "success": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)






class CreateOrderView(APIView):
    def post(self, request):
        user = self.request.user
        serializer = CorpPackageWriteSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        package = serializer.save(created_by=user, created_by_role=user.role, sender_user=user)



        # documents handling
        for file in request.FILES.getlist("package_attachments"):
            PackageAttachment.objects.create(package=package, attachment=file)

        
        return Response({ "success": True, "id": package.id, "message": "Package created successfully"})




class CorporateOrdersView(generics.ListCreateAPIView):
    serializer_class = CorpPackageReadSerializer
    queryset = Package.objects.all()
    permission_classes = [ IsAuthenticated, IsOwnerOrAdmin ]

    def get_queryset(self):
        user = self.request.user
        return Package.objects.filter(
            Q(created_by=user)
        ).distinct().order_by('-created_at')




class CorpPackageRetrieveEditDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CorpPackageReadSerializer
    queryset = Package.objects.all()
    permission_classes = [ IsAuthenticated, IsOwnerOrAdmin ]
    lookup_field = "slug"

    def get_object(self):
        try:
            return super().get_object()

        except:
            return Response({ "success": False, "message": "Package not found with this slug."})


    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "message": "Package retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            "success": True,
            "message": "Package updated successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        return Response({
            "success": True,
            "message": "Package deleted successfully."
        }, status=status.HTTP_204_NO_CONTENT)
    





