from django.urls import path
from apps.payments.views import *


urlpatterns = [
    path( "invoices/", AllInvoicesView.as_view(), name="invoices", ),
]


