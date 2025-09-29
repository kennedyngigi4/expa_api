import uuid
from django.db import models
from apps.accounts.models import User
# Create your models here.



class VehicleType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name
    

class DistanceBand(models.Model):
    name = models.CharField(max_length=200)
    min_km = models.DecimalField(max_digits=10, decimal_places=2)
    max_km = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.min_km} - {self.max_km} km"


class WeightTier(models.Model):
    name = models.CharField(max_length=100)  
    min_weight = models.DecimalField(max_digits=8, decimal_places=2)
    max_weight = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.min_weight}–{self.max_weight} tons)"



class VehiclePricing(models.Model):
    vehicle = models.ForeignKey(VehicleType, on_delete=models.CASCADE, related_name="vehicle_pricing_rules")
    band = models.ForeignKey(DistanceBand, on_delete=models.CASCADE, related_name="rates", null=True) 
    weight = models.ForeignKey(WeightTier, on_delete=models.CASCADE, related_name="tiers", null=True)
    
    # base price in kms
    base_distance = models.DecimalField(max_digits=10, decimal_places=2, help_text="km included in base price", null=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="base price", null=True)
    extra_per_km = models.DecimalField(max_digits=10, decimal_places=2, help_text="kes", null=True)


    class Meta:
        unique_together = (
            "vehicle", "weight", "band", 
        )


    def __str__(self):
        return f"{self.vehicle.name} | {self.weight.name} | {self.band.name}"
    


class Booking(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customer")
    vehicle = models.ForeignKey(VehicleType, on_delete=models.SET_NULL, null=True, related_name="booked_vehicle")
    pickup_address = models.CharField(max_length=255)
    dropoff_address = models.CharField(max_length=255)
    distance =  models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.sender.full_name} booked {self.vehicle.name}"



