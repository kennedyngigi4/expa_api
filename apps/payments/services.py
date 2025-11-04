from django.db import transaction
from django.db.models import Q
from apps.payments.models import Invoice, ConsolidatedInvoice



@transaction.atomic
def consolidated_invoices(client, invoice_ids, admin_user):
    invoices = Invoice.objects.filter(Q(status__in=["pending", "unpaid"]), user=client, id__in=invoice_ids)

    if not invoices.exists():
        raise ValueError("No valid pending invoices found for this client.")

    total = sum(inv.amount for inv in invoices)

    consolidated = ConsolidatedInvoice.objects.create(
        client=client, total_amount=total, generated_by=admin_user
    )
    consolidated.invoices.set(invoices)

    invoices.update(status='consolidated', parent_invoice=None)
    return consolidated

