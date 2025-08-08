import os
import uuid
import qrcode
import string
import random
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.db import transaction
from django.db.models import Max, Min
from django.utils.text import slugify
import qrcode.constants
from apps.accounts.models import Office, User, DriverLocation, PartnerProfile
from geopy.distance import geodesic
# Create your models here.


class County(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class SizeCategory(models.Model):

    TYPE_CHOICES = [
        ( 'parcel', 'Parcel', ),
        ( 'package', 'Package', ),
    ]

    name = models.CharField(max_length=50, choices=TYPE_CHOICES, unique=True)
    max_length = models.PositiveIntegerField()
    max_width = models.PositiveIntegerField()
    max_height = models.PositiveIntegerField()
    description = models.TextField()
    base_price = models.DecimalField(max_digits=15, decimal_places=4)

    def __str__(self):
        return self.name


class PackageType(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("name"))
    price = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name
    

class UrgencyLevel(models.Model):
    name = models.CharField(max_length=50, unique=True) 
    description = models.TextField(blank=True)
    
    
    surcharge_type = models.CharField(
        max_length=10,
        choices=[('fixed', 'Fixed'), ('percent', 'Percentage')],
        default='fixed'
    )
    surcharge_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="If percentage, use 10 for 10%"
    )

    def __str__(self):
        return self.name



class IntraCityParcelPolicy(models.Model):
    max_weight = models.DecimalField(max_digits=10, decimal_places=2, default=15.00)
    max_distance_km = models.PositiveIntegerField(default=35)
    base_km = models.PositiveIntegerField(default=5)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=350.00)
    extra_price_per_km = models.DecimalField(max_digits=10, decimal_places=2, default=35.00)

    def __str__(self):
        return f"Intracity Parcel policy"
    

class IntraCityPackagePricing(models.Model):
    min_weight = models.DecimalField(max_digits=10, decimal_places=2)  # in kg
    max_weight = models.DecimalField(max_digits=10, decimal_places=2)  # in kg
    base_price = models.DecimalField(max_digits=12, decimal_places=2)  # for first 5km
    extra_km_price = models.DecimalField(max_digits=12, decimal_places=3)  # per km after 5km

    def __str__(self):
        return f"{self.min_weight}-{self.max_weight}kg"



class InterCountyRoute(models.Model):
    origins = models.ManyToManyField(Office, related_name="intercounty_route_origins")
    destinations = models.ManyToManyField(Office, related_name="intercounty_route_destinations")
    size_category = models.ForeignKey(SizeCategory, on_delete=models.CASCADE)
    
    base_weight_limit = models.DecimalField(max_digits=10, decimal_places=2, default=10)
    base_price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        origins = ", ".join([office.name for office in self.origins.all()])
        destinations = ", ".join([office.name for office in self.destinations.all()])
        return f"{origins} ➝ {destinations} [{self.size_category.name}]"
    

class InterCountyWeightTier(models.Model):
    route = models.ForeignKey(InterCountyRoute, on_delete=models.CASCADE, related_name='tiers')
    min_weight = models.DecimalField(max_digits=10, decimal_places=2)
    max_weight = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.min_weight}-{self.max_weight}kg @ {self.price_per_kg}/kg"



class LastMileDeliveryPolicy(models.Model):
    office = models.OneToOneField(Office, on_delete=models.CASCADE, related_name="last_mile_policy")
    free_within_km = models.DecimalField(max_digits=5, decimal_places=2, default=2.5)
    per_km_fee = models.DecimalField(max_digits=10, decimal_places=2, default=30.00)

    def __str__(self):
        return f"Last Mile Policy - {self.office.name}"




def generateID(pref):
    random_id = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"{pref}{random_id}"

def UserPackageImgPath(instance, filename):
    user_id = str(instance.created_by.id).replace("-","")
    return f"packages/{user_id}/{filename}"


class PackageStatus(models.TextChoices):
    PENDING = "PENDING", "PENDING"
    ASSIGNED = "ASSIGNED", "ASSIGNED"
    IN_TRANSIT = "IN_TRANSIT", "IN_TRANSIT"
    DELIVERED = "DELIVERED", "DELIVERED"
    RECEIVED = "RECEIVED", "RECEIVED"
    RETURNED = "RETURNED", "RETURNED"
    CANCELLED = "CANCELLED", "CANCELLED"
    HANDOVER = "HANDOVER", "HANDOVER"


class Package(models.Model):

    DELIVERY_TYPES = [
        ( "intra_city", 'Intra-City', ),
        ( 'inter_county', 'Inter-County', ),
        ( 'international', 'International', ),
    ]


    id = models.UUIDField(unique=True, editable=False, primary_key=True, default=uuid.uuid4, verbose_name=_("unique ID"))
    slug = models.SlugField(unique=True, null=True, blank=True)
    package_id = models.CharField(max_length=100, unique=True, null=True,)
    package_number = models.PositiveIntegerField(unique=True, null=True, blank=True)

    size_category = models.ForeignKey(SizeCategory, on_delete=models.SET_NULL, null=True)
    delivery_type = models.CharField(max_length=20, choices=DELIVERY_TYPES, verbose_name=_("delivery type"))

    name = models.CharField(max_length=255, verbose_name=_("name")) 
    package_type = models.ForeignKey(PackageType, on_delete=models.SET_NULL, null=True, verbose_name=_("package type"))
    is_fragile = models.BooleanField(default=False, verbose_name=_("fragile"))
    urgency = models.ForeignKey(UrgencyLevel, on_delete=models.SET_NULL, null=True, verbose_name=_("urgency"))
    length = models.IntegerField(null=True, blank=True, verbose_name=_("length"))
    width = models.IntegerField(null=True, blank=True, verbose_name=_("width"))
    height = models.IntegerField(null=True, blank=True, verbose_name=_("height"))
    weight = models.IntegerField(null=True, blank=True, verbose_name=_("weight"))
    pickup_date = models.DateTimeField(null=True, blank=True, verbose_name=_("pickup date time"))
    description = models.TextField(verbose_name=_("description"))
    fees = models.DecimalField(max_digits=15, decimal_places=6, null=True, verbose_name=_("fee charged"))
    image = models.ImageField(upload_to=UserPackageImgPath, null=True, blank=True, verbose_name=_("package image"))

    sender_name = models.CharField(max_length=255, null=True, verbose_name=_("sender name") )
    sender_phone = models.CharField(max_length=20, verbose_name=_("sender phone"))
    sender_address = models.CharField(max_length=255, verbose_name=_("sender address"))
    sender_latLng = models.CharField(max_length=70, verbose_name=_("sender latitude,longitude"))
    

    recipient_name = models.CharField(max_length=60, verbose_name=_("recipient name"))
    recipient_phone = models.CharField(max_length=20, verbose_name=_("recipient phone"))
    recipient_address = models.CharField(max_length=255, verbose_name=_("recipient location"))
    recipient_latLng = models.CharField(max_length=70, verbose_name=_("recipient latitude,longitude"))
    origin_office = models.ForeignKey(Office, null=True, blank=True, on_delete=models.SET_NULL, related_name='origin_packages')
    destination_office = models.ForeignKey(Office, null=True, blank=True, on_delete=models.SET_NULL, related_name='destination_packages')

    current_handler = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='handling_packages')
    delivery_stage_count = models.PositiveIntegerField(default=1)
    current_stage = models.PositiveIntegerField(default=1)
    requires_pickup = models.BooleanField(default=False)
    requires_last_mile = models.BooleanField(default=False, help_text="If True, deliver to recipient's door. Else recipient picks from destination office.")
    is_returned = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_packages')
    created_by_role = models.CharField(max_length=30, blank=True, null=True)
    sender_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='sent_packages')
    status = models.CharField(max_length=30, choices=PackageStatus.choices, default=PackageStatus.PENDING,)

    def save(self, *args, **kwargs):
        if not self.package_id:
            while True:
                new_id = generateID("EX")
                if not Package.objects.filter(package_id=new_id).exists():
                    self.package_id = new_id
                    break

        if self.package_number is None:
            with transaction.atomic():
                last_number = Package.objects.select_for_update().aggregate(Max('package_number'))['package_number__max'] or 0
                self.package_number = last_number + 1

        if not self.slug:
            base = slugify(self.name)
            unique_suffix = str(uuid.uuid4())[:10]
            self.slug = f"{base}-{unique_suffix}"

        if not self.origin_office:
            try:
                lat, lng = map(float, self.sender_latLng.split(','))
                self.origin_office = self.get_nearest_office(lat, lng)
            except Exception as e:
                print(f"Error parsing sender coordinates: {e}")

        if not self.destination_office:
            try:
                lat, lng = map(float, self.recipient_latLng.split(','))
                self.destination_office = self.get_nearest_office(lat, lng)
            except Exception as e:
                print(f"Error parsing recipient coordinates: {e}")

        super().save(*args, **kwargs)


    @staticmethod
    def get_nearest_office(lat, lng):
        offices = Office.objects.all()
        package_coords = (float(lat), float(lng))

        nearest = None
        min_distance = float("inf")

        for office in offices:
            office_coords = (float(office.geo_lat), float(office.geo_lng))
            distance = geodesic(package_coords, office_coords).km

            if distance < min_distance:
                min_distance = distance
                nearest = office
        return nearest

    
    class Meta:
        indexes = [
            models.Index(fields=['created_by']),
            models.Index(fields=['sender_user']),
            models.Index(fields=['delivery_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Package to {self.recipient_name}"


def ShipmentQRPath(instance, filename):
    return f"shipments/qr_codes/{filename}"

class Shipment(models.Model):

    SHIPMENT_TYPES = [
        ( 'delivery', 'Delivery to Recipient', ),
        ( 'pickup', 'Pickup to Office', ),
        ( 'transfer', 'Office to Office Transfer', ),
        ( 'complete', 'Pickup and Deliver to Recipient'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shipment_id = models.CharField(max_length=100, unique=True, null=True)
    shipment_number = models.PositiveIntegerField(unique=True, blank=True, null=True)

    shipment_type = models.CharField(max_length=60, choices=SHIPMENT_TYPES)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='managers', null=True, limit_choices_to={'role': 'manager'})
    courier = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='couriers', null=True, limit_choices_to={'role__in': ['driver', 'partner_rider']})
    packages = models.ManyToManyField(Package, through='ShipmentPackage', related_name='shipments')

    status = models.CharField(max_length=50, default='created')
    delivery_stage_count = models.PositiveIntegerField(default=1)
    current_stage = models.PositiveIntegerField(default=1)

    requires_handover = models.BooleanField(default=False)
    assigned_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    confirm_received = models.BooleanField(default=False)

    origin_office = models.ForeignKey(Office, related_name="shipment_origin", on_delete=models.CASCADE, null=True, blank=True)
    destination_office = models.ForeignKey(Office, related_name="shipment_destination", on_delete=models.CASCADE, null=True, blank=True)

    qrcode_svg = models.FileField(upload_to=ShipmentQRPath, null=True)


    def save(self, *args, **kwargs):
        if not self.shipment_id:
            while True:
                new_id = generateID("SH")
                if not Shipment.objects.filter(shipment_id=new_id).exists():
                    self.shipment_id = new_id
                    break

        if self.shipment_number is None:
            with transaction.atomic():
                last_number = Shipment.objects.select_for_update().aggregate(
                    Max('shipment_number')
                )['shipment_number__max'] or 0
                self.shipment_number = last_number + 1

        if not self.qrcode_svg:
            self.generateQRCode()

        super().save(*args, **kwargs)

    
    def generateQRCode(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4
        )

        qr.add_data(self.shipment_id)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back="white")

        # construct filepath
        file_name = f"{self.shipment_id}.png"
        file_path = os.path.join(settings.MEDIA_ROOT, "shipments/qr_codes", file_name)

        # ensure qrcodes directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # SVG File
        img.save(file_path)

        # save relative path
        self.qrcode_svg.name = f"shipments/qr_codes/{file_name}"


    def __str__(self):
        return f"Shipment {self.shipment_id}"



class ShipmentStage(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name="stages")
    stage_number = models.PositiveIntegerField()
    driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role__in': ['driver', 'partner_rider']})
    from_office = models.ForeignKey(Office, on_delete=models.SET_NULL, null=True, blank=True, related_name='stage_from')
    to_office = models.ForeignKey(Office, on_delete=models.SET_NULL, null=True, blank=True, related_name='stage_to')
    status = models.CharField(max_length=30, choices=[
        ("pending", "Pending"),
        ("in_transit", "In Transit"),
        ("completed", "Completed"),
    ], default="pending")

    handover_required = models.BooleanField(null=True, blank=True)
    driver_accepted = models.BooleanField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    

    class Meta:
        unique_together = ("shipment", "stage_number")
        ordering = ['stage_number']

    def __str__(self):
        return f"Stage {self.stage_number} of Shipment {self.shipment.shipment_id}"




class ShipmentPackage(models.Model):
    DELIVERY_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('delivered', 'Delivered'),
        ('returned', 'Returned to Office'),
        ('failed', 'Delivery Failed'),
    ]

    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE)
    package = models.ForeignKey(Package, on_delete=models.CASCADE)

    status = models.CharField(max_length=30, choices=DELIVERY_STATUS_CHOICES, default='pending')
    delivered = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    confirmed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='confirmed_packages')
    confirmed_at = models.DateTimeField(null=True, blank=True)
    receiver_signature = models.ImageField(upload_to='signatures/', null=True, blank=True)


    pickup_stage = models.ForeignKey(
        ShipmentStage, null=True, blank=True, on_delete=models.SET_NULL, related_name="pickup_packages"
    )
    delivery_stage = models.ForeignKey(
        ShipmentStage, null=True, blank=True, on_delete=models.SET_NULL, related_name="delivery_packages"
    )

    # Optional: If this package has a pickup from address or partner shop
    pickup_address = models.TextField(null=True, blank=True)
    pickup_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="pickup_packages")
    pickup_shop = models.ForeignKey(PartnerProfile, null=True, blank=True, on_delete=models.SET_NULL)

    # Optional: If this package is being delivered directly to someone
    delivery_address = models.TextField(null=True, blank=True)
    delivery_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="delivery_packages")




    class Meta:
        unique_together = ('shipment', 'package')

    def __str__(self):
        return f"{self.package} in {self.shipment} - {self.status}"




class ShipmentTracking(models.Model):
    shipment_stage = models.ForeignKey(ShipmentStage, on_delete=models.CASCADE, null=True, related_name='tracking_logs')
    location = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    status_update = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Tracking shipment of {self.shipment.id}"





class HandOver(models.Model):

    HANDOVER_TYPE_CHOICES = [
        ( 'package', 'Package', ),
        ( 'shipment', 'Shipment', ),
    ]

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
    handover_type = models.CharField(max_length=10, choices=HANDOVER_TYPE_CHOICES)
    shipment_stage = models.ForeignKey(ShipmentStage, on_delete=models.CASCADE, null=True, related_name="handovers")

    stage_number = models.PositiveIntegerField()
    from_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='handover_from')
    to_users = models.ManyToManyField(User, related_name='handover_to')
    confirmed_by = models.ManyToManyField(User, related_name='handover_confirmed', blank=True)

    is_partner = models.BooleanField(default=False)
    partner_name = models.CharField(max_length=255, null=True, blank=True)

    location = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('handover_type', 'stage_number')

    def __str__(self):
        return f"{self.id}"




