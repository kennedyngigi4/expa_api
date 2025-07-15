from django.urls import path
from apps.accounts.superadmin.views import *


urlpatterns = [
    path( "offices/", OfficeView.as_view(), name="offices", ),
    path( "office_details/<str:pk>/", OfficeDetailsUpdateDeleteView.as_view(), name="offices", ),
    path( "users/", AllUsersView.as_view(), name="users", ),
]


