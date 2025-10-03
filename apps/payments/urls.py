from django.urls import path
from apps.payments.views import *
from apps.payments.mpesa import *


urlpatterns = [
    path("customer_invoices/", InvoicesView.as_view(), name="customer_invoices", ),
    path("payments", MPESA, name="payments", ),
    path("callback/", PaymentCallbackView.as_view(), name="callback", ),
    path("invoices/<str:invoice_id>/", generate_invoice_pdf, name="generate_invoice_pdf")

]


