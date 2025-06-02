from django.contrib import admin
from apps.accounts.models import *
# Register your models here.


admin.site.register(User)
admin.site.register(Profile)
admin.site.register(DriverLocation)
