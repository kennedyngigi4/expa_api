from django.db import models
# Create your models here.



class CorporateAccount(models.Model):
    company_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, null=True)
    contact_person = models.CharField(max_length=255, null=True)
    address = models.CharField(max_length=15, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.company_name}"



class CorporateOffice(models.Model):
    corporate_account = models.ForeignKey(CorporateAccount, on_delete=models.CASCADE, related_name="corporate_office")
    name = models.CharField(max_length=255, null=True)
    phone = models.CharField(max_length=15, null=True)
    contact_person = models.CharField(max_length=255, null=True)
    address = models.CharField(max_length=15, null=True)
    lat_lng = models.CharField(max_length=60, null=True)
    is_active = models.BooleanField(default=True)
    is_head_office = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.corporate_account.company_name} - {self.name}"


class CorporateRoute(models.Model):
    # origin and destination routes
    origin_office = models.ForeignKey("accounts.Office", on_delete=models.CASCADE, related_name="corp_pricing_origin")
    destination_office = models.ForeignKey("accounts.Office", on_delete=models.CASCADE, related_name="corp_pricing_destination")


    def __str__(self):
        return f"{self.origin_office} -> {self.destination_office}"


class CorporateRoutePricing(models.Model):
    corporate_account = models.ForeignKey(CorporateOffice, on_delete=models.CASCADE, null=True, related_name="pricing_tiers")
    route = models.ForeignKey(CorporateRoute, on_delete=models.CASCADE, related_name="corporate_tiers", null=True)

    min_weight = models.DecimalField(max_digits=10, decimal_places=2, help_text="kgs")
    max_weight = models.DecimalField(max_digits=10, decimal_places=2, help_text="kgs")

    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="kes")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = (
            "corporate_account", "route", "min_weight", "max_weight"
        )


    def __str__(self):
        return f"{self.route} | {self.min_weight}-{self.max_weight}kg"
