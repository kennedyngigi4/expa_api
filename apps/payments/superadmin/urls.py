from django.urls import path
from apps.payments.superadmin.views import *


urlpatterns = [
    path('all/', AllPaymentsView.as_view(), name='all/', ),
]

