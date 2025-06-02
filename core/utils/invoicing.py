from decimal import Decimal
from django.db import transaction
from apps.payments.models import Invoice, Payment
from apps.logistics.models import Order, OrderDetails



def create_invoice(account, orders, created_by=None, commit=True):
    """
        Generate an invoice for the provided account and list of orders
    """

    orders = list(orders)

    if not orders:
        raise ValueError("No orders provided for invoicing.")

    total = sum(Decimal(order.price) for order in orders)
    try:
        # with transaction.atomic():
            invoice = Invoice.objects.create(
                customer=account,
                total_amount=total,
                status="UNPAID",
                created_by=created_by
            )
            

            if commit:
                invoice.save()

                invoice.order = [order.id for order in orders ]
                invoice.save()

                # Update orders to reflect they have been paid
                for order in orders:
                    try:
                        order_details = OrderDetails.objects.get(order=order)
                        order_details.invoice_id = invoice.id
                        order_details.is_invoiced = True
                        order_details.save()
                    except OrderDetails.DoesNotExist:
                        OrderDetails.objects.create(
                            order=order,
                            invoice_id=invoice.id,
                            is_invoiced=True
                        )
            return invoice
    except Exception as e:
        print("Error occurred:", e)

