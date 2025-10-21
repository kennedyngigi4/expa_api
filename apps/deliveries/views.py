import math
import googlemaps
from django.shortcuts import render
from django.db.models import Q
from django.conf import settings
from django.db.models import Sum

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.response import Response

from geopy.distance import geodesic
from decimal import Decimal, ROUND_HALF_UP

from apps.accounts.models import *
from apps.accounts.permissions import *
from apps.deliveries.models import *
from apps.deliveries.serializers import *
from apps.payments.models import *
from core.utils.payments import NobukPayments
from core.utils.emails import send_order_creation_email
from apps.messaging.utils import send_notification

gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
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



class BusinessAccountStatsView(APIView):
    permission_classes = [ IsAuthenticated ]

    def get(self, request):
        user = self.request.user

        if user.account_type != "business":
            return Response({ "success": False, "message": "Not a business account."}, status=403)
        

        # Total orders by this business
        all_orders = Package.objects.filter(created_by=user).count()

        # unpaid_invoices
        unpaid_qs = Invoice.objects.filter(Q(status__iexact="unpaid") | Q(status__iexact="pending"), package__created_by=user)
        unpaid_invoices = unpaid_qs.count()

        # total unpaid amounts
        total_amount_unpaid = unpaid_qs.aggregate(total=Sum("amount"))["total"] or 0


        return Response({
            "all_orders": all_orders,
            "unpaid_invoices": unpaid_invoices,
            "total_amount_unpaid": total_amount_unpaid
        })



class AddOrderView(generics.CreateAPIView):
    serializer_class = PackageWriteSerializer
    queryset = Package.objects.all()
    permission_classes = [ IsAuthenticated, IsOwnerOrAdmin ]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            
            if serializer.is_valid():
                
                user = self.request.user

                order = serializer.save(
                    created_by=self.request.user,
                    created_by_role=self.request.user.role,
                    sender_user=user,
                )

                # payable_amount = request.data["fees"]
                # mpesa_number = request.data["payment_phone"]
                # invoice = Invoice.objects.get(package=order)
                # if invoice:
                #     # Initiate STKPush payments 
                #     if user.account_type == "personal": 
                #         if request.data["payment_method"] == "mpesa":
                #             NobukPayments(mpesa_number, user.full_name, invoice.invoice_id, payable_amount, "web").STKPush()
                #         elif request.data["payment_method"] == "card":
                #             print("Card ", request.data["cardholder_name"])
                   

                # # Send creation email
                # send_order_creation_email(user, order)
                # send_notification(user, f"Order {order.package_id}", "You order was submitted successfully.")

                return Response({
                    "success": True,
                    "message": "Package created successfully.",
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


class CustomerPackagesView(generics.ListAPIView):
    serializer_class = PackageSerializer
    queryset = Package.objects.all()
    permission_classes = [ IsAuthenticated, IsOwnerOrAdmin ]

    def get_queryset(self):
        user = self.request.user
        return Package.objects.filter(
            Q(created_by=user)
        ).distinct().order_by('-created_at')
    

    


class CustomerPackageRetrieveEditDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PackageSerializer
    queryset = Package.objects.all()
    permission_classes = [ IsAuthenticated, IsOwnerOrAdmin ]
    lookup_field = "slug"

    def get_object(self):
        try:
            return super().get_object()

        except:
            raise NotFound(detail="Package not found with this slug.")


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
        }, status=status.HTTP_200_OK)






def get_road_distance_km(origin, destination):
   
    try:
        result = gmaps.distance_matrix(origins=[origin], destinations=[destination], mode="driving", units="metric")
        element = result['rows'][0]['elements'][0]

        if element.get('status') != 'OK':
            return None
        
        distance_meters = element['distance']['value']
        return round(Decimal(distance_meters) / 1000, 2)
    except Exception:
        return None



def calculate_volumetric_weight(length_cm, width_cm, height_cm, divisor=6000):
    return (length_cm * width_cm * height_cm ) / divisor


def calculate_chargeable_weight(actual_weight_kg, length_cm, width_cm, height_cm):
    volumetric_weight = calculate_volumetric_weight(length_cm, width_cm, height_cm)
    return max(actual_weight_kg, volumetric_weight)


def is_within_region(lat, lng, center_lat, center_lng, radius_km):
    origin = f"{center_lat},{center_lng}"
    destination = f"{lat},{lng}"

    try:
        result = gmaps.distance_matrix(origins=[origin], destinations=[destination], mode="driving", units="metric")
        element = result['rows'][0]['elements'][0] 

        if element.get('status') != 'OK':
            return False
        
        distance_meters = element['distance']['value']
        distance_km = Decimal(distance_meters) / 1000

        return distance_km <= Decimal(radius_km)
    except Exception as e:
        return False


class IntraCityPriceCalculationView(APIView):
    def post(self, request):
        data = request.data

        try:
            size_category = SizeCategory.objects.get(id=data.get("size_category"))
            weight = Decimal(data.get("weight", 0))
            length = Decimal(data.get("length", 0))
            width = Decimal(data.get("width", 0))
            height = Decimal(data.get("height", 0))

            sender_latLng = data.get("sender_latLng")
            recipient_latLng = data.get("recipient_latLng")
            if not sender_latLng or not recipient_latLng:
                return Response({"success": False, "message": "Sender and recipient locations are required."})

            sender_coords = tuple(round(float(coord), 5) for coord in sender_latLng.split(","))
            recipient_coords = tuple(round(float(coord), 5) for coord in recipient_latLng.split(","))

            distance_km = get_road_distance_km(sender_coords, recipient_coords)
            if distance_km is None:
                return Response({ "success": False, "message": "Failed to calculate road distance." }, status=500)


            # Policy check
            valid_policy = None
            for policy in IntraCityParcelPolicy.objects.select_related("office"):
                office = policy.office
                if not (office.geo_lat and office.geo_lng):
                    continue


                lat_c, lng_c = float(office.geo_lat), float(office.geo_lng)
                
                sender_in_radius = is_within_region(sender_coords[0], sender_coords[1], lat_c, lng_c, policy.radius_km)
                recipient_in_radius = is_within_region(recipient_coords[0], recipient_coords[1], lat_c, lng_c, policy.radius_km)

                if sender_in_radius or recipient_in_radius:
                    valid_policy = policy
                    break
            
            if not valid_policy:
                return Response({
                    "success": False,
                    "message": "Pickup and dropoff must be within the same city/office zone for intracity delivery. Try intercounty instead."
                }, status=status.HTTP_400_BAD_REQUEST)
            
            policy = valid_policy
            
            # Pricing logic
            if size_category.name.lower() == "parcel":
                if weight > policy.max_weight:
                    return Response({ "success": False, "message": "Parcel exceeds max weight." }, status=400)
                
                if distance_km > policy.max_distance_km:
                    return Response({ "success": False, "message": "Distance exceeds max intracity coverage." }, status=400)

                if distance_km <= policy.base_km:
                    price = policy.base_price

                else:
                    extra_km = distance_km - Decimal(policy.base_km)
                    price = policy.base_price + (extra_km * policy.extra_price_per_km)


            elif size_category.name.lower() == "package":
                chargeable_weight = calculate_chargeable_weight(weight, length, width, height)
                chargeable_weight = Decimal(chargeable_weight).quantize(Decimal("1.00"), rounding=ROUND_HALF_UP)

                pricing = IntraCityPackagePricing.objects.filter(
                    min_weight__lte=chargeable_weight,
                    max_weight__gte=chargeable_weight
                ).first()

                if not pricing:
                    return Response({ "success": False, "message": "No pricing rule for this weight bracket." }, status=400)

                base_km = policy.base_km
                if distance_km <= base_km:
                    price = pricing.base_price

                else:
                    extra_km = distance_km - Decimal(base_km)
                    price = pricing.base_price + (extra_km * pricing.extra_km_price)

            else:
                return Response({ "success": False, "message": "Invalid size_category." }, status=400)

            
            return Response({
                "success": True,
                "distance_km": round(distance_km, 2),
                "total_fee": round(price)
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
            requires_last_mile = bool(data.get("requires_last_mile"))
            requires_pickup = bool(data.get("requires_pickup"))

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
            chargeable_weight = calculate_chargeable_weight(weight, length, width, height)

            # Match route
            size_category = SizeCategory.objects.get(id=size_category_id)
            route, created = InterCountyRoute.get_or_create_bidirectional(
                origin_office=origin_office,
                destination_office=destination_office,
                size_category=size_category
            )


            if not route:
                return Response({
                    "success": False,
                    "message": "No intercounty route pricing found for selected path."
                }, status=404)
            
            
            # base_price = route.base_price
            # base_limit = route.base_weight_limit

            
            if chargeable_weight:
                tier = InterCountyWeightTier.objects.filter(
                    route=route,
                    min_weight__lte=chargeable_weight,
                    max_weight__gte=chargeable_weight
                ).first()
                

                if not tier:
                    return Response({
                        "success": False,
                        "message": "No matching tier for excess weight."
                    }, status=404)

                total_price = chargeable_weight * tier.price_per_kg
            

            # Calculate pickup fee if required
            pickup_fee = Decimal("0.00")
            if requires_pickup and origin_office.enable_pickup:
                pickup_distance_km = get_road_distance_km(sender_coords, (float(origin_office.geo_lat),float(origin_office.geo_lng)))
                pickup_distance_km = Decimal(round(pickup_distance_km, 2))

                chargeable_weight = calculate_chargeable_weight(chargeable_weight, length, width, height)
                print(chargeable_weight)
                pricing = IntraCityPackagePricing.objects.filter(
                    min_weight__lte=chargeable_weight,
                    max_weight__gte=chargeable_weight
                ).first()

                print(pricing)

                if pricing:
                    max_km = origin_office.max_pickup_km

                    
                    if pickup_distance_km <= max_km:
                        pickup_fee = pricing.base_price
                        
                    else:
                        extra_distance = pickup_distance_km - max_km
                        pickup_fee = pricing.base_price + (extra_distance * pricing.extra_km_price)
                    
                    discount_rate = origin_office.pickup_discount_percent / Decimal("100.00")
                    pickup_discount = pickup_fee * discount_rate
                    pickup_fee -= pickup_discount



            # ✅ Calculate last mile fee if required
            last_mile_fee = Decimal("0.00")
            if requires_last_mile:
                last_mile_fee = self.get_lastmile_price(destination_office, recipient_coords)
            
            final_fee = pickup_fee + total_price + last_mile_fee

            return Response({
                "success": True,
                "pickup_fee": round(pickup_fee),
                "base_fee": round(total_price),
                "last_mile_fee": round(last_mile_fee),
                "total_fee": round(final_fee),
                "origin_office_id": origin_office.id,
                "destination_office_id": destination_office.id,
                "chargeable_weight": round(chargeable_weight, 2),
                
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


