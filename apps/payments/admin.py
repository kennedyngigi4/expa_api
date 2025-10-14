from django.contrib import admin
from apps.payments.models import *
# Register your models here.


admin.site.register(Invoice)
admin.site.register(Payment)
admin.site.register(PaymentsLog)
