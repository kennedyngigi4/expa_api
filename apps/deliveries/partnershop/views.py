from django.shortcuts import render
from decimal import Decimal

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import *
from apps.accounts.permissions import *
from apps.deliveries.models import *
from apps.deliveries.partnershop.serializers import *
from apps.payments.mpesa import MPESA


class PackageUploadView(generics.ListCreateAPIView):
    serializer_class = PackageWriteSerializer
    permission_classes = [IsAuthenticated, IsPartnerPickup]

    def get_queryset(self):
        user = self.request.user
        queryset = Package.objects.filter(created_by=user).order_by("-created_at")
        return queryset
    
    
    def post(self, request, *args, **kwargs):
        user = self.request.user

        try:
            partner_profile = user.partner_profile
        except PartnerProfile.DoesNotExist:
            return Response({
                "success": False,
                "message": "Partner profile not found."
            }, status=status.HTTP_400_BAD_REQUEST)


        office = partner_profile.office
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                created_by=user,
                created_by_role=user.role,
                sender_user=user,
                origin_office=office,
                sender_address=office.geo_loc,
                sender_latLng=f"{office.geo_lat}, {office.geo_lng}"
            )
            MPESA(request.data["sender_phone"], request.data["fees"]).MpesaSTKPush()
            return Response({ "success": True, "message" : "Upload successful."}, status=status.HTTP_201_CREATED)
        
        return Response({ "success": False, "message": serializer.errors }, status=status.HTTP_400_BAD_REQUEST)





class IntraCityPriceCalculationView(APIView):
    permission_classes = [ IsAuthenticated, IsPartnerPickup]

    def post(self, request):
        data = request.data
        user = self.request.user

        try:
            size_category = data.get("size_category")
            size_category = SizeCategory.objects.get(id=size_category)
            weight = Decimal(data.get("weight", 0))
            sender_latLng = user.partner_profile.location_latLang
            recipient_latLng = data.get("recipient_latLng")

            sender_coords = tuple(round(float(coord), 5) for coord in sender_latLng.split(","))
            recipient_coords = tuple(round(float(coord), 5) for coord in recipient_latLng.split(","))

            distance_km = geodesic(sender_coords, recipient_coords).km
            distance_km = Decimal(distance_km)
            

            if size_category.name.lower() == "parcel":
                
                policy = IntraCityParcelPolicy.objects.first()
                
                if weight > policy.max_weight:
                    print(distance_km)
                    return Response({ "success": False, "message": "Parcel exceeds max weight." }, status=400)
                
                if distance_km > policy.max_distance_km:
                    return Response({ "success": False, "message": "Distance exceeds max range for parcel delivery." }, status=400)

                if distance_km <= policy.base_km:
                    
                    price = policy.base_price

                else:
                    extra_km = distance_km - Decimal(policy.base_km)
                    price = policy.base_price + (extra_km * policy.extra_price_per_km)

                
                

            elif size_category.name.lower() == "package":
                pricing = IntraCityPackagePricing.objects.filter(
                    min_weight__lte=weight,
                    max_weight__gte=weight
                ).first()

                if not pricing:
                    return Response({ "error": "No pricing rule for this weight bracket." }, status=400)

                if distance_km <= 5:
                    price = pricing.base_price
                else:
                    extra_km = distance_km - Decimal(5)
                    price = pricing.base_price + (extra_km * pricing.extra_km_price)

            else:
                return Response({ "success": False, "message": "Invalid size_category." }, status=400)

            
            return Response({
                "success": True,
                "distance_km": round(distance_km, 2),
                "estimated_fee": round(price, 2)
            })

        except Exception as e:
            return Response({ "success": False, "message": str(e) }, status=500)

