import json
import googlemaps
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


gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)


# Views come here

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
            
            return Response({ "success": True, "message" : "Upload successful."}, status=status.HTTP_201_CREATED)
        
        return Response({ "success": False, "message": serializer.errors }, status=status.HTTP_400_BAD_REQUEST)




def get_road_distance_km(origin, destination):
    result = gmaps.distance_matrix(origins=[origin], destinations=[destination], mode="driving")
    try:
        distance_meters = result['rows'][0]['elements'][0]['distance']['value']  # meters
        return round(Decimal(distance_meters) / 1000, 2)  # km
    except Exception:
        return None


def calculate_volumetric_weight(length_cm, width_cm, height_cm, divisor=6000):
    return (length_cm * width_cm * height_cm ) / divisor


def calculate_chargeable_weight(actual_weight_kg, length_cm, width_cm, height_cm):
    volumetric_weight = calculate_volumetric_weight(length_cm, width_cm, height_cm)
    return max(actual_weight_kg, volumetric_weight)



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

            distance_km = get_road_distance_km(sender_coords, recipient_coords)
            
            

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







class InterCountyPriceCalculator(APIView):
    def post(self, request):
        user = self.request.user

        try:
            data = request.data
            
            size_category_id = data.get("size_category")
            weight = Decimal(data.get("weight", 0))
            length = Decimal(data.get("length", 0))
            width = Decimal(data.get("width", 0))
            height = Decimal(data.get("height", 0))
            requires_last_mile = bool(data.get("requires_last_mile", False))
            requires_pickup = bool(data.get("requires_pickup", False))
            

            sender_latLng = user.partner_profile.location_latLang
            recipient_latLng = data.get("recipient_latLng")

            if not sender_latLng or not recipient_latLng:
                return Response({ "success": False, "message": "Missing coordinates." })
            
            # convert to coordinates tuples
            sender_coords =  tuple(round(float(coord), 5) for coord in sender_latLng.split(","))
            recipient_coords = tuple(round(float(coord), 5) for coord in recipient_latLng.split(","))

            # get nearest offices
            origin_office = user.partner_profile.office
            destination_office = get_nearest_office(recipient_coords)

            if not origin_office or not destination_office:
                return Response({ "success": False, "message": "Could not resolve nearest offices." }, status=404)
            
            # Calculate chargeable weight
            chargeable_weight = calculate_chargeable_weight(weight, length, width, height)

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
                print(requires_last_mile)
                last_mile_fee = self.get_lastmile_price(destination_office, recipient_coords)

                print("Last mile ....")
                print(last_mile_fee)
            
            final_fee =  total_price + last_mile_fee

            return Response({
                "success": True,
                "estimated_fee": round(total_price),
                "last_mile_fee": round(last_mile_fee),
                "total_fee": round(final_fee),
                "origin_office_id": origin_office.id,
                "destination_office_id": destination_office.id,
                "chargeable_weight": round(chargeable_weight, 2),
                "base_limit": base_limit
            })


        except Exception as e:
            return Response({ "success": False, "message": str(e) }, status=500)



    def get_lastmile_price(self, office, recipient_coords):
        try:
            
            policy = office.last_mile_policy 
        except LastMileDeliveryPolicy.DoesNotExist:
            return Decimal("0.00") 
        
        office_coord = (float(office.geo_lat),float(office.geo_lng))
        
        distance_km = get_road_distance_km(office_coord, recipient_coords)
        distance_km = Decimal(round(distance_km, 2))

        if distance_km <= policy.free_within_km:
            return Decimal("0.00")

        
        extra_km = distance_km - policy.free_within_km
        
        return extra_km * policy.per_km_fee



