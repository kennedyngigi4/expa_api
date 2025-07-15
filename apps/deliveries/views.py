import math
from django.shortcuts import render
from django.db.models import Q

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from geopy.distance import geodesic
from decimal import Decimal

from apps.accounts.models import *
from apps.accounts.permissions import *
from apps.deliveries.models import *
from apps.deliveries.serializers import *
from apps.payments.mpesa import MPESA

# Create your views here.



class SizeCategoryView(generics.ListAPIView):
    serializer_class = SizeCategorySerializer
    queryset = SizeCategory.objects.all()


class PackageTypeView(generics.ListAPIView):
    serializer_class = PackageTypeSerializer
    queryset = PackageType.objects.all().order_by("name")


class UrgencyView(generics.ListAPIView):
    serializer_class = UrgencyLevelSerializer
    queryset = UrgencyLevel.objects.all().order_by("name")



class CustomerPackagesView(generics.ListCreateAPIView):
    serializer_class = PackageWriteSerializer
    queryset = Package.objects.all()
    permission_classes = [ IsAuthenticated, IsOwnerOrAdmin ]

    def get_queryset(self):
        user = self.request.user
        return Package.objects.filter(
            Q(created_by=user)
        ).distinct().order_by('-created_at')
    

    def post(self, request, *args, **kwargs):
        
        serializer = self.get_serializer(data=request.data)
        
        
       
        try:
            

            if serializer.is_valid():
                user = self.request.user

                serializer.save(
                    created_by=self.request.user,
                    created_by_role=self.request.user.role,
                    sender_user=user,
                )
                
                MPESA(request.data["sender_phone"], request.data["fees"]).MpesaSTKPush()
                
                return Response({
                    "success": True,
                    "message": "Package created successfully.",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            
                
            return Response({ "success": False, "message": serializer.errors }, status=status.HTTP_400_BAD_REQUEST)




        except ValidationError as ve:
            return Response({
                "success": False,
                "message": "Validation error occurred.",
                "errors": ve.detail
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "success": False,
                "message": f"An error occurred: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class CustomerPackageRetrieveEditDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PackageSerializer
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






class IntraCityPriceCalculationView(APIView):
    def post(self, request):
        data = request.data
        
        try:
            size_category = data.get("size_category")
            size_category = SizeCategory.objects.get(id=size_category)
            weight = Decimal(data.get("weight", 0))
            sender_latLng = data.get("sender_latLng")
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
                "estimated_fee": round(price)
            })

        except Exception as e:
            return Response({ "success": False, "message": str(e) }, status=500)






class InterCountyPriceCalculator(APIView):
    def post(self, request):
        try:
            data = request.data
            size_category_id = data.get("size_category")
            weight = Decimal(data.get("weight", 0))
            length = Decimal(data.get("length", 0))
            width = Decimal(data.get("width", 0))
            height = Decimal(data.get("height", 0))
            requires_last_mile = data.get("requires_last_mile", False)

            sender_latLng = data.get("sender_latLng")
            recipient_latLng = data.get("recipient_latLng")

            if not sender_latLng or not recipient_latLng:
                return Response({ "success": False, "message": "Missing coordinates." })
            
            # convert to coordinates tuples
            sender_coords =  tuple(round(float(coord), 5) for coord in sender_latLng.split(","))
            recipient_coords = tuple(round(float(coord), 5) for coord in recipient_latLng.split(","))

            # get nearest offices
            origin_office = get_nearest_office(sender_coords)
            destination_office = get_nearest_office(recipient_coords)

            if not origin_office or not destination_office:
                return Response({ "success": False, "message": "Could not resolve nearest offices." }, status=404)
            
            # Calculate chargeable weight
            volumetric_weight = (length * width * height) / Decimal(6000)
            chargeable_weight = max(weight, volumetric_weight)

            

            # Match route
            route = InterCountyRoute.objects.filter(
                origins=origin_office,
                destinations=destination_office,
                size_category_id=size_category_id
            ).first()

            if not route:
                return Response({
                    "success": False,
                    "message": "No intercounty route pricing found for selected path."
                }, status=404)
            
            
            base_price = route.base_price
            base_limit = route.base_weight_limit

            
            if chargeable_weight <= base_limit:
                total_price = base_price

            else:
                
                excess_weight = chargeable_weight - base_limit
                
                tier = InterCountyWeightTier.objects.filter(
                    route=route,
                    min_weight__lte=excess_weight,
                    max_weight__gte=excess_weight
                ).first()
                

                if not tier:
                    return Response({
                        "success": False,
                        "message": "No matching tier for excess weight."
                    }, status=404)

                total_price = base_price + (excess_weight * tier.price_per_kg)

            
            # ✅ Calculate last mile fee if required
            last_mile_fee = Decimal("0.00")
            if requires_last_mile:
                last_mile_fee = self.get_lastmile_price(destination_office, recipient_coords)

            final_fee = total_price + last_mile_fee

            return Response({
                "success": True,
                "estimated_fee": round(total_price),
                "last_mile_fee": round(last_mile_fee),
                "total_fee": round(final_fee),
                "origin_office_id": origin_office.id,
                "destination_office_id": destination_office.id,
                "chargeable_weight": round(chargeable_weight, 2),
                "volumetric_weight": round(volumetric_weight, 2),
                "base_limit": base_limit
            })


        except Exception as e:
            return Response({ "success": False, "message": str(e) }, status=500)



    def get_lastmile_price(self, office, recipient_coords):

        try:
            policy = office.last_mile_policy 
        except LastMileDeliveryPolicy.DoesNotExist:
            return Decimal("0.00") 

        office_coord = (float(office.geo_lat), float(office.geo_lng))
        distance_km = geodesic(office_coord, recipient_coords).km
        distance_km = Decimal(round(distance_km, 2))

        if distance_km <= policy.free_within_km:
            return Decimal("0.00")

        extra_km = distance_km - policy.free_within_km
        return extra_km * policy.per_km_fee


def get_nearest_office(coords):
    offices = Office.objects.all()

    nearest = None
    min_distance = float("inf")

    for office in offices:
        try:
            distance = geodesic(coords, (float(office.geo_lat), float(office.geo_lng))).km
            if distance < min_distance:
                min_distance = distance
                nearest = office
        except Exception:
            continue

    return nearest


