from django.urls import path
from apps.payments.views import *
from apps.payments.mpesa import *


urlpatterns = [
    path("customer_invoices/", InvoicesView.as_view(), name="customer_invoices", ),
    path("payments", MPESA, name="payments", ),
]


