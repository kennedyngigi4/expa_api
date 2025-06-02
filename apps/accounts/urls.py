from django.urls import path
from rest_framework_simplejwt.views import ( TokenObtainPairView, TokenRefreshView )
from apps.accounts.views import *

urlpatterns = [
    path( "register/", RegistrationView.as_view(), name="register", ),
    path( "login/", LoginView.as_view(), name='login', ),
    path( "refresh/", TokenRefreshView.as_view(), name="refresh", ),
    path( "employees/", AllEmployeesView.as_view(), name="employees", ),
    path( "drivers/", AllDriversView.as_view(), name="drivers", ),
    path( "clients/", AllClients.as_view(), name="clients", ),
    path( "user_details/<str:pk>/", UserDetails.as_view(), name="user_details", ),
    path( "profile/", UserProfileView.as_view(), name="profile", ),
]



