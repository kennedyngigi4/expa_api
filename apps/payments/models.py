import uuid
from django.db import models
from apps.accounts.models import *
from apps.deliveries.models import *
from django.contrib.auth import get_user_model

user = get_user_model()
# Create your models here.


class Invoice(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, unique=True, default=uuid.uuid4)
    invoice_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    package = models.OneToOneField(Package, related_name="invoice", null=True, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=14, decimal_places=4)
    status = models.CharField(max_length=60, default='unpaid')
    issued_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.invoice_id:
            while True:
                new_id = generateID("IN")
                if not Invoice.objects.filter(invoice_id=new_id).exists():
                    self.invoice_id = new_id
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice_id}"



class Payment(models.Model):
    PAYMENT_METHODS = [
        ( 'mpesa', 'M-PESA', ),
        ( 'airtel_money', 'Airtel Money', ),
        ( 'card', 'Card', ),
        ( 'bank_transfer', 'Bank Transfer', ),
        ( "cash", "Cash Payment"),
    ]


    PAYMENT_STATUS = [
        ( 'pending', 'pending', ),
        ( 'successful', 'Successful', ),
        ( 'failed', 'Failed', ),
    ]

    id = models.UUIDField(primary_key=True, editable=False, unique=True, default=uuid.uuid4)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)

    payer_name = models.CharField(max_length=100)
    payer_phone = models.CharField(max_length=20)
    
    payment_method = models.CharField(max_length=100, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=100, choices=PAYMENT_STATUS)
    reference = models.CharField(max_length=100, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    received_by = models.ForeignKey(
        User, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        related_name='received_cash_payments',
        help_text="Staff who confirmed the cash payment"
    )

    def __str__(self):
        return f"{self.reference} - {self.status}"
    



class PaymentsLog(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return str(self.created_at)


