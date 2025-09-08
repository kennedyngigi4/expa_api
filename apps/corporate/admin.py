from django.contrib import admin

from apps.corporate.models import *
# Register your models here.


admin.site.register(CorporateAccount)
admin.site.register(CorporateOffice)
admin.site.register(CorporateRoute)
admin.site.register(CorporateRoutePricing)
