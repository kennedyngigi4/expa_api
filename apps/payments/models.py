import uuid
from django.db import models
from apps.accounts.models import *
from apps.deliveries.models import *
from django.contrib.auth import get_user_model

user = get_user_model()
# Create your models here.


class Invoice(models.Model):

    STATUS_CHOICES = [
        ('paid', 'paid',),
        ('pending', 'pending',),
        ('consolidated', 'consolidated',),
        ('cancelled', 'cancelled',),
    ]

    id = models.UUIDField(primary_key=True, editable=False, unique=True, default=uuid.uuid4)
    invoice_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    package = models.OneToOneField(Package, related_name="invoice", null=True, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=14, decimal_places=4)
    status = models.CharField(max_length=60, default='unpaid')
    issued_at = models.DateTimeField(auto_now_add=True)
    parent_invoice = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='child_invoices')

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



class ConsolidatedInvoice(models.Model):
    STATUS_CHOICES = [
        ('paid', 'paid',),
        ('consolidated', 'consolidated',),
    ]

    id = models.UUIDField(primary_key=True, editable=False, unique=True, default=uuid.uuid4)
    consolidated_invoice_id = models.CharField(max_length=100, unique=True)
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="consolidated_invoices")
    invoices = models.ManyToManyField(Invoice, related_name="consolidations")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=60, choices=STATUS_CHOICES, null=True, default='consolidated')
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_consolidations")


    def save(self, *args, **kwargs):
        if not self.consolidated_invoice_id:
            while True:
                new_id = generateID("CIN")
                if not ConsolidatedInvoice.objects.filter(consolidated_invoice_id=new_id).exists():
                    self.consolidated_invoice_id = new_id
                    break
        super().save(*args, **kwargs)


    def __str__(self):
        return f"Consolidated Invoice {self.consolidated_invoice_id} - {self.client}"



class Payment(models.Model):
   
    id = models.UUIDField(primary_key=True, editable=False, unique=True, default=uuid.uuid4)
    invoice_id = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True)
    amount = models.CharField(max_length=28, null=True)
    transaction_code = models.CharField(max_length=255, null=True)
    customer_name = models.CharField(max_length=255, null=True)
    phone_number = models.CharField(max_length=50, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.transaction_code


class PaymentsLog(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    invoice_id = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True)
    data = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return str(self.created_at)


