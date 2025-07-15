from django.contrib import admin
from apps.accounts.models import *
# Register your models here.


admin.site.register(User)
admin.site.register(Office)
admin.site.register(PartnerProfile)
admin.site.register(DriverLocation)

