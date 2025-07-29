from django.urls import path
from apps.accounts.views import *


urlpatterns = [
    path( 'register/', RegistrationView.as_view(), name='register', ),
    path( 'login/', LoginView.as_view(), name='login', ),
    path( 'profile/', ProfileView.as_view(), name='profile', ),
]


urlpatterns += [
    path( "offices/", OfficeView.as_view(), name="offices",),
    path( "couriers/", CouriersView.as_view(), name="couriers", ),
]


