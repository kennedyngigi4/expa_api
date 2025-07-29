from django.shortcuts import render
from django.template.loader import select_template, render_to_string
from django.http import HttpResponse

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError


from apps.payments.models import *
from apps.payments.serializers import *
# Create your views here.


class InvoicesView(generics.ListAPIView):
    serializer_class = InvoiceSerializer
    queryset = Invoice.objects.all().order_by("-issued_at")
    permission_classes = [ IsAuthenticated ]


    def get_queryset(self):
        user = self.request.user
        queryset = Invoice.objects.filter(user=user)
        return queryset




def generate_invoice_pdf(request, invoice_id):
    invoice = Invoice.objects.select_related("package").get(id=invoice_id)

    # html_string = render_to_string("payments/invoice_pdf.html", { "invoice": invoice})
    # pdf_file = HTML(string=html_string).write_pdf()

    # response = HttpResponse(pdf_file, content_type='application/pdf')
    # response['Content-Disposition'] = f'filename=invoice_{invoice.id}.pdf'
    # return response



