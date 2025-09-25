from django.contrib import admin
from apps.drivers.models import *
# Register your models here.

admin.site.register(DriverDevice)
admin.site.register(Wallet)
admin.site.register(WalletTransaction)
