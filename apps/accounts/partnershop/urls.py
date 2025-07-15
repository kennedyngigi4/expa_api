from django.urls import path
from apps.accounts.partnershop.views import *


urlpatterns = [
    path( "statistics/", PartnerShopStatisticsView.as_view(), name="statistics", ),
]

