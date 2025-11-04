import os
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.colors import red, green, white, black
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.staticfiles import finders

from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from apps.accounts.models import *
from apps.accounts.permissions import IsAdmin
from apps.payments.models import *
from apps.payments.serializers import *
from apps.payments.services import consolidated_invoices


class AllPaymentsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all().order_by("-date_created")



class AdminConsolidationView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, *args, **kwargs):
        client_id = request.data.get("client_id")
        invoice_ids = request.data.get("invoice_ids")

        if not client_id or not invoice_ids:
            return Response({ "success": False, "message": "Client and invoices are required." }, status=status.HTTP_400_BAD_REQUEST)

        try:
            client = User.objects.get(id=client_id)
            consolidated = consolidated_invoices(client, invoice_ids, request.user)
            serializer = ConsolidatedInvoiceSerializer(consolidated)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except User.DoesNotExist:
            return Response({ "success": False, "message": "Client not found." }, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({ "success": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class AdminConsolidatedInvoices(APIView):
    permission_classes = [IsAdmin, IsAuthenticated]

    def get(self, request):
        user = request.user

        consolidated_invoices = ConsolidatedInvoice.objects.filter(generated_by=user)
        serialized_invoices = ConsolidatedInvoiceSerializer(consolidated_invoices, many=True)

        consolidated_count = ConsolidatedInvoice.objects.filter(status="consolidated").count()
        paid_count = ConsolidatedInvoice.objects.filter(status="paid").count()

        data = {
            "consolidated_count": consolidated_count,
            "paid_count": paid_count,
            "serialized_invoices": serialized_invoices.data,
        }

        return Response(data)





def draw_status(canvas, doc, status):
    width, height = A4

    # Choose colors based on status
    if status and status.lower() == "paid":
        bg_color = colors.green
        text_color = colors.white
        label = "PAID"
    else:
        bg_color = colors.red
        text_color = colors.white
        label = "UNPAID"

    canvas.saveState()

    # Move near top right corner
    canvas.translate(width - 110, height - -20)

    # Rotate ~330 degrees
    canvas.rotate(320)

    # Draw rectangle (strip)
    canvas.setFillColor(bg_color)
    canvas.rect(0, 0, 200, 30, fill=1, stroke=0)

    # Add text
    canvas.setFillColor(text_color)
    canvas.setFont("Helvetica-Bold", 14)
    canvas.drawCentredString(90, 8, label)

    canvas.restoreState()


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def generate_consinvoice_pdf(request, consolidated_id):
    consolidated = get_object_or_404(ConsolidatedInvoice, id=consolidated_id)

    

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    logo_path = finders.find("payments/images/logo.png")

    # Logo and company header
    if logo_path and os.path.exists(logo_path):
        logo = Image(logo_path, width=140, height=60)
        logo.hAlign = "LEFT"
        elements.append(logo)
        

    # --- Header ---
    expa = Paragraph("Express Parcel", styles["Heading2"])
    expa_contacts = Paragraph("0722 620 988 / 0734 620 988")
    expa_payments = Paragraph("Consolidated Invoice Details")
    elements.extend([expa, expa_contacts, expa_payments, Spacer(1, 30)])

    # --- Recipient Info ---
    recipient_name = Paragraph(f"{request.user.full_name}", styles["Heading4"])
    recipient_email = Paragraph(f"{request.user.email}")
    elements.extend([recipient_name, recipient_email, Spacer(1, 20)])

    # --- Invoice Meta ---
    invoice_id_para = Paragraph(f"#{consolidated.consolidated_invoice_id}", styles["Heading3"])
    invoice_issued_date = Paragraph(f"<b>Date Issued:</b> {consolidated.created_at.strftime('%Y-%m-%d')}")
    elements.extend([invoice_id_para, invoice_issued_date, Spacer(1, 25)])

    # --- Linked Invoices ---
    # Assuming consolidated.invoices is a ManyToManyField or list of IDs
    if hasattr(consolidated, "invoices") and consolidated.invoices:
        invoice_ids = list(consolidated.invoices.values_list("id", flat=True)) if hasattr(consolidated.invoices, "values_list") else consolidated.invoices
        all_invoices = Invoice.objects.filter(id__in=invoice_ids)
    else:
        all_invoices = Invoice.objects.none()

    # Table header
    data = [["Invoice ID", "Description", "Amount (KES)"]]

    total_amount = 0
    for inv in all_invoices:
        desc = inv.name if hasattr(inv, "name") and inv.name else "Parcel / Delivery Service"
        data.append([str(inv.invoice_id), desc, f"{inv.amount:,.2f}"])
        total_amount += inv.amount

    # Add total row
    data.append(["", "Total", f"{total_amount:,.2f}"])

    # Table Styling
    table = Table(data, colWidths=[160, 250, 100])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
    ]))
    elements.append(table)

    # --- Footer ---
    elements.append(Spacer(1, 30))
    center_style = styles["Normal"].clone("center_style")
    center_style.alignment = TA_CENTER
    center_style.fontSize = 9
    generated_on = datetime.now().strftime("%Y-%m-%d %H:%M")
    footer_note = Paragraph(f"PDF generated on {generated_on}", center_style)
    elements.append(footer_note)

    # --- Build PDF with watermark/status ---
    doc.build(
        elements,
        onFirstPage=lambda canvas, doc: draw_status(canvas, doc, getattr(consolidated, "status", "unpaid")),
        onLaterPages=lambda canvas, doc: draw_status(canvas, doc, getattr(consolidated, "status", "unpaid")),
    )

    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="consolidated_invoice_{consolidated.consolidated_invoice_id}.pdf"'
    return response





