from django.urls import path
from apps.accounts.views import *


urlpatterns = [
    path( 'register/', RegistrationView.as_view(), name='register', ),
    path( 'login/', LoginView.as_view(), name='login', ),
    path( "password-reset-request/", PasswordResetRequestView.as_view(), name="password_reset_request", ),
    path( "password-reset-confirm/", PasswordResetConfirmView.as_view(), name="password_reset_confirm", ),
    path( 'profile/', ProfileView.as_view(), name='profile', ),
]


urlpatterns += [
    path( "offices/", OfficeView.as_view(), name="offices",),
    path( "couriers/", CouriersView.as_view(), name="couriers", ),
]


