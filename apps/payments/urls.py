from django.urls import path
from apps.payments.views import *
from apps.payments.mpesa import *


urlpatterns = [
    path("customer_invoices/", InvoicesView.as_view(), name="customer_invoices", ),
    path("payments", MPESA, name="payments", ),
    path("invoices/<uuid:invoice_id>/pdf/", generate_invoice_pdf, name="generate_invoice_pdf")

]


