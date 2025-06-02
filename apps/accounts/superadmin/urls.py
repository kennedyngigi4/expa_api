from django.urls import path
from apps.accounts.superadmin.views import *
from rest_framework.routers import DefaultRouter


routers = DefaultRouter()
routers.register(r"updateuser", AdminUpdateUserProfileView, basename="updateuser", ),
urlpatterns = routers.urls

urlpatterns += [
    path( "register_employee/", CreateEmployeeView.as_view(), name="register_employee", ),
]

