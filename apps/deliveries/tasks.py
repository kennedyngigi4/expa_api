import logging
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from core.utils.services import *
from django.utils import timezone
import datetime
from apps.deliveries.models import Package
from apps.messaging.views import intracity_drivers_notification
from apps.messaging.utils import send_notification
from django.db import transaction


logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def send_intracity_notifications(self, package_id, delay=60):
    try:
        package = Package.objects.select_related("origin_office").get(id=package_id)
    except Package.DoesNotExist:
        logger.warning(f"⚠️ Package {package_id} not found when sending notifications.")
        return

    # Skip if already handled
    if package.status in ["assigned", "in_transit", "delivered"]:
        logger.info(f"✅ Package {package.package_id} already accepted, skipping notification.")
        return

    # Validate location
    if not package.sender_latLng:
        logger.warning(f"⚠️ Missing sender location for {package.package_id}")
        return

    try:
        lat, lng = package.sender_latLng.split(",")
        pickup_coords = (float(lat.strip()), float(lng.strip()))
    except ValueError:
        logger.error(f"❌ Invalid sender lat/lng for {package.package_id}")
        return

    # Get nearby drivers
    drivers = get_nearby_drivers(pickup_coords, radius_km=10)
    if drivers:
        # Send notifications to drivers
        intracity_drivers_notification(
            drivers=drivers,
            title="🚚 New Intracity Order",
            body=f"Pickup at {package.sender_address}",
            data={"type": "new_order", "order_id": str(package.id)},
        )
        logger.info(f"📣 Notified {len(drivers)} drivers for package {package.package_id}")

        # Schedule acceptance check after DB commit (avoids race condition)
        transaction.on_commit(
            lambda: check_order_acceptance.apply_async(args=[package.id], countdown=delay)
        )
        logger.info(f"⏱ Scheduled acceptance check for {package.package_id} in {delay}s")

    else:
        logger.warning(f"⚠️ No drivers nearby for {package.package_id}, escalating immediately.")
        _escalate_to_manager(package)


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def check_order_acceptance(self, package_id):
    try:
        package = Package.objects.select_related("origin_office").get(id=package_id)
    except Package.DoesNotExist:
        logger.warning(f"⚠️ Package {package_id} not found for acceptance check.")
        return

    package.refresh_from_db()
    logger.warning(f"🔍 Checking package {package.package_id} status={package.status}")

    if package.status not in ["assigned", "in_transit", "delivered"]:
        logger.error(f"🚨 Package {package.package_id} still not accepted. Escalating to manager.")
        _escalate_to_manager(package)
    else:
        logger.info(f"✅ Package {package.package_id} accepted, no escalation needed.")


def _escalate_to_manager(package):
    logger.warning(f"🚨 Escalation triggered for package {package.package_id}")

    if not package.origin_office:
        logger.warning(f"⚠️ No origin office for {package.package_id}, cannot escalate.")
        return

    managers = User.objects.filter(role__iexact="manager", office=package.origin_office)
    if not managers.exists():
        logger.warning(f"⚠️ No managers found for office {package.origin_office}.")
        return

    for manager in managers:
        try:
            send_notification(
                user=manager,
                title="⚠️ No Driver Accepted Order",
                message=f"No driver accepted delivery of {package.package_id}. Please assign manually.",
            )
            logger.info(f"📤 Escalation notification sent to manager {manager.id}")
        except Exception as e:
            logger.exception(f"❌ Failed to send escalation notification to manager {manager.id}: {e}")

    logger.warning(f"🚨 Escalated to {managers.count()} manager(s) for package {package.package_id}")