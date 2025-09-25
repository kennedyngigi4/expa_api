from django.db import models
from django.conf import settings

from apps.accounts.models import User
from apps.deliveries.models import Shipment
# Create your models here.


class DriverDevice(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="device"
    )
    fcm_token = models.CharField(max_length=255, unique=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.fcm_token[:20]}"



class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wallet")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def credit(self, amount):
        self.balance += amount
        self.save()

    def debit(self, amount):
        if amount > self.balance:
            raise ValueError("Insufficient balance")
        
        self.balance -= amount
        self.save()

    def __str__(self):
        return f"{self.user.full_name} - Balance: {self.balance}"



class WalletTransaction(models.Model):
    TRANSACTION_TYPES = [
        ("credit", "Credit"),
        ("debit", "Debit"),
    ]


    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transactions")
    shipment = models.ForeignKey(Shipment, on_delete=models.SET_NULL, null=True, blank=True, related_name="wallet_transactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    note = models.TextField(null=True, blank=True)


    def __str__(self):
        return f"{self.wallet.user.full_name} - {self.transaction_type} {self.amount}"


