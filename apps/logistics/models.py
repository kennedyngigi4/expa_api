import os
import uuid
import random
import string
import barcode
import qrcode
from django.db import models
from barcode.writer import SVGWriter
from django.conf import settings
from django.db import transaction
from django.db.models import Max, Min
import qrcode.constants

# Create your models here.


class Route(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name



class Warehouse(models.Model):
    wid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255, null=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    county = models.CharField(max_length=255, null=True, blank=True)
    subcounty = models.CharField(max_length=255, null=True, blank=True)
    longitude = models.CharField(max_length=25, null=True, blank=True)
    latitude = models.CharField(max_length=25, null=True, blank=True)
    email = models.EmailField(null=True)
    phone = models.CharField(max_length=30, null=True, blank=True)
    storage_type = models.CharField(max_length=100, null=True, blank=True)
    total_storage = models.CharField(max_length=100, null=True, blank=True)
    available_storage = models.CharField(max_length=200, null=True, blank=True)
    loading_bays = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=60, null=True, blank=True)
    created_by = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.name} - {self.location}"



def generateOrderID():
    random_id = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"EX{random_id}"


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    package_name = models.CharField(max_length=255, null=True, blank=True)
    delivery_type = models.CharField(max_length=60, null=True, blank=True)
    freight_type = models.CharField(max_length=60, null=True, blank=True)
    fragile = models.CharField(max_length=30, null=True, blank=True)
    urgency = models.CharField(max_length=30, null=True, blank=True)
    length = models.CharField(max_length=30, null=True, blank=True)
    width = models.CharField(max_length=30, null=True, blank=True)
    height = models.CharField(max_length=30, null=True, blank=True)
    weight = models.CharField(max_length=255, null=True, blank=True)
    sender_fullname = models.CharField(max_length=60, null=True, blank=True)
    sender_email = models.CharField(max_length=60, null=True, blank=True)
    sender_phone = models.CharField(max_length=60, null=True, blank=True)
    pickup_datetime = models.CharField(max_length=60, null=True, blank=True)
    pickup_location = models.TextField(null=True, blank=True)
    pickup_latLng = models.CharField(max_length=40, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    recipient_fullname = models.CharField(max_length=60, null=True, blank=True)
    recipient_email = models.CharField(max_length=60, null=True, blank=True)
    recipient_phone = models.CharField(max_length=60, null=True, blank=True)
    recipient_location = models.TextField(null=True, blank=True)
    recipient_latLng = models.CharField(max_length=40, null=True, blank=True)
    order_id = models.CharField(max_length=60, null=True, unique=True, blank=True)
    order_number = models.IntegerField(unique=True, blank=True, null=True)
    price = models.CharField(max_length=60, null=True, blank=True)


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, null=True, blank=True)


    def save(self, *args, **kwargs):
        using_db = kwargs.get('using') or 'logistics'
        if not self.order_id:
            while True:
                new_id = generateOrderID()
                if not Order.objects.filter(order_id=new_id).exists():
                    self.order_id = new_id
                    break

        if self.order_number is None:
            with transaction.atomic(using=using_db):
                last_order = Order.objects.select_for_update().aggregate(Max('order_number'))['order_number__max'] or 0
                self.order_number = last_order + 1
        
        super().save(*args, **kwargs)


    def __str__(self):
        return self.order_id


class OrderDetails(models.Model):
    order_details_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    order = models.OneToOneField(Order, related_name="details", on_delete=models.CASCADE, null=True)
    transaction_id = models.CharField(max_length=200, null=True, blank=True)
    payment_method = models.CharField(max_length=200, null=True, blank=True)
    pickup_confirmed = models.BooleanField(default=False)
    assigned_pickupto = models.CharField(max_length=255, null=True, blank=True)
    delivery_stage = models.CharField(max_length=200, default="PENDING",  null=True, blank=True)
    delivery_status = models.CharField(max_length=200, default="UPDATING ...", null=True, blank=True)
    invoice_id = models.CharField(max_length=255, null=True, blank=True)
    is_invoiced = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return str(self.order.order_id)
    


def ImagePath(instance, filename):
    order_id = str(instance.order.id).replace("-","")
    return f"orders/{order_id}/{filename}"


class OrderImages(models.Model):
    order = models.ForeignKey(Order, related_name="images", on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to=ImagePath, null=True, blank=True)


    def __str__(self):
        return str(self.order.order_id)




def generateShipmentNumber():
    # unique shipment number generator ends with EX
    unique_number = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"SN-{unique_number}EX"


def barcodesPath(instance, filename):
    return f"barcodes/{filename}"

class Shipment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    shipment_number = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, null=True, blank=True)
    assigned_to = models.CharField(max_length=255, null=True, blank=True)
    delivery_stage = models.CharField(max_length=70, null=True, blank=True)
    delivery_status = models.CharField(max_length=70, null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    total_shipment_stages = models.IntegerField(default=1)
    completed_shipment_stages = models.IntegerField(default=0)
    shipment_route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True)
    shipment_type = models.CharField(max_length=100, null=True, blank=True)
    barcode_svg = models.FileField(upload_to=barcodesPath, null=True, blank=True)
    partner_sharing = models.BooleanField(default=False, null=True, blank=True)
    partner = models.CharField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.shipment_number:
            while True:
                new_shipmentnumber = generateShipmentNumber()
                if not Shipment.objects.filter(shipment_number=new_shipmentnumber).exists():
                    self.shipment_number = new_shipmentnumber
                    break

        if not self.barcode_svg:
            self.generateQRCode()

        super().save(*args, **kwargs)


    def generateQRCode(self):
        
        # generate barcode from shipment number
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4
        )
        qr.add_data(self.shipment_number)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back="white")

        # construct filepath
        file_name = f"{self.shipment_number}.png"
        file_path = os.path.join(settings.MEDIA_ROOT, "barcodes", file_name)

        # ensure barcodes directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # SVG File
        img.save(file_path)

        # save relative path
        self.barcode_svg.name = f"barcodes/{file_name}"
        

    def __str__(self):
        return f"{self.shipment_number}"



class ShipmentItems(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    order = models.ForeignKey(Order, related_name="orders", on_delete=models.CASCADE, null=True)
    shipment = models.ForeignKey(Shipment, related_name="items", on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=50, default='pending')
    assigned_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.id}"



class ShipmentLeg(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    shipment = models.ForeignKey(Shipment, related_name="legs", on_delete=models.CASCADE, null=True)
    driver = models.CharField(max_length=255, null=True, blank=True)
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=50, default="PROCESSING", null=True, blank=True)
    starttime = models.DateTimeField(auto_now=True, blank=True, null=True)
    completedtime = models.DateTimeField(auto_now=True, blank=True, null=True)
    active = models.BooleanField(default=False)
    created_by = models.CharField(max_length=255, null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return str(self.id)





class Incident(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, null=True)
    message = models.TextField(null=True)
    driver = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return str(self.shipment.shipment_number)

