import googlemaps
from django.conf import settings
from decimal import Decimal
from apps.deliveries.models import VehicleType, VehiclePricing


gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)


def get_road_distance_km(origin, destination):
    result = gmaps.distance_matrix(origins=[origin], destinations=[destination], mode="driving")
    try:
        distance_meters = result['rows'][0]['elements'][0]['distance']['value']  # meters
        return round(Decimal(distance_meters) / 1000, 2)  # km
    except Exception:
        return None



def calculate_volumetric_weight(length_cm, width_cm, height_cm, divisor=6000):
    return (length_cm * width_cm * height_cm ) / divisor



def calculate_vehicle_price(vehicle_type, weight, distance):

    rule = VehiclePricing.objects.filter(
        vehicle_type=vehicle_type,
        min_weight__lte=weight,
        max_weight__gte=weight,
        min_distance__lte=distance,
        max_distance__gte=distance
    ).first()

    if not rule:
        raise ValueError("No vehicle pricing rule found for this vehicle, weight, and distance.")
    
    # start with base price
    price = rule.base_price

    # check if distance is above base distance
    if distance > rule.base_distance:
        extra_km = distance - rule.base_distance
        price += extra_km * rule.price_per_extra_km

    return price

