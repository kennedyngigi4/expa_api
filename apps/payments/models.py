import uuid
import random
import string
from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.


class Payment(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    transaction_id = models.CharField(max_length=30, unique=True, null=True, blank=True)
    payment_method = models.CharField(max_length=60, null=True, blank=True)
    amount = models.IntegerField(default=0)
    phone_number = models.CharField(max_length=30, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_id}"


def generateInvoiceID():
    random_id = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"IN{random_id}"


class Invoice(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    is_paid = models.BooleanField(default=False)
    customer = models.CharField(max_length=255, null=True, blank=True)
    invoice_id = models.CharField(max_length=20, null=True, blank=True)
    order = ArrayField(models.UUIDField(), default=list, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, default=0, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, default=0, decimal_places=2)
    status = models.CharField(max_length=60, null=True, blank=True)
    created_by = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    due_date = models.DateTimeField(auto_now=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.invoice_id:
            while True:
                new_id = generateInvoiceID()
                if not Invoice.objects.filter(invoice_id=new_id).exists():
                    self.invoice_id = new_id
                    break
        super().save(*args, **kwargs)


    def __str__(self):
        return str(self.invoice_id)


