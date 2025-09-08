import googlemaps
from django.conf import settings
from geopy.distance import geodesic
from apps.accounts.models import *


gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)


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




def get_road_distance_km(origin, destination):
    result = gmaps.distance_matrix(origins=[origin], destinations=[destination], mode="driving")
    try:
        distance_meters = result['rows'][0]['elements'][0]['distance']['value']  # meters
        return round(Decimal(distance_meters) / 1000, 2)  # km
    except Exception:
        return None




