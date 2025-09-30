from celery import shared_task
from core.utils.services import *
from django.utils import timezone
import datetime
from apps.deliveries.models import Package
from apps.messaging.views import intracity_drivers_notification
from apps.messaging.utils import send_notification

@shared_task
def send_intracity_notifications(package_id):
    try:
        package = Package.objects.get(id=package_id)
    except Package.DoesNotExist:
        return "Package not found"
    
    if not package.sender_latLng:
        return "No sender location details"


    try:
        lat, lng = package.sender_latLng.split(",")
        pickup_coords = (float(lat.strip()), float(lng.strip()))
    except ValueError:
        return "Invalid latlng format"


    drivers = get_nearby_drivers(pickup_coords, radius_km=5)

    if drivers:
        intracity_drivers_notification(
            drivers=drivers,
            title="🚚 New Intracity Order",
            body=f"Pickup at {package.sender_address}",
            data={"type": "new_order", "order_id": str(package.id)},
        )
        return f"Notified {len(drivers)} drivers"
    

    if package.origin_office:
        managers = User.objects.filter(
            role="manager",
            office=package.origin_office,
        )

        for manager in managers:
            send_notification(
                user=manager,
                title="⚠️ No Driver Available",
                message=f"No drivers were available for delivery of {package.package_id}"
            )
            return "No drivers nearby"




