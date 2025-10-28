from django.urls import path
from apps.accounts.superadmin.views import *


urlpatterns = [
    path( "statistics/", CompanyStatisticsView.as_view(), name="statistics", ),
    path( "offices/", OfficeView.as_view(), name="offices", ),
    path( "office_details/<str:pk>/", OfficeDetailsUpdateDeleteView.as_view(), name="offices", ),
    path( "users/", AllUsersView.as_view(), name="users", ),
    path( "user_details/<uuid:user_id>/", UserDetailsView.as_view(), name="user-details", ),
]


