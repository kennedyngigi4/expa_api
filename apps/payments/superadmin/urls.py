from django.urls import path
from apps.payments.superadmin.views import *


urlpatterns = [
    path('all/', AllPaymentsView.as_view(), name='all/', ),
    path("consolidate/", AdminConsolidationView.as_view(), name="consolidate", ),
    path("consolidated_invoices/", AdminConsolidatedInvoices.as_view(), name="consolidated_invoices", ),
    path("consolidated-pdf/<str:consolidated_id>/", generate_consinvoice_pdf, name="consolidated-pdf", ),
]

