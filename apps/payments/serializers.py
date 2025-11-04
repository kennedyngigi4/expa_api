from rest_framework import serializers
from apps.payments.models import *


class InvoiceSerializer(serializers.ModelSerializer):

    package_name = serializers.SerializerMethodField()
    client = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = [
            'id', "invoice_id", "package", "package_name", "amount", "status", "issued_at", "client"
        ]

        read_only_fields = [
            "user", "client"
        ]

    def get_package_name(self, obj):
        return obj.package.package_id
    

    def get_client(self, obj):
        user = getattr(obj, "user", None)
        if not user:
            return None
        
        return {
            "id": user.id,
            "name": user.full_name
        }


class ConsolidatedInvoiceSerializer(serializers.ModelSerializer):
    invoices = InvoiceSerializer(many=True, read_only=True)
    client_name = serializers.SerializerMethodField()

    class Meta:
        model = ConsolidatedInvoice
        fields = [
            "id", "consolidated_invoice_id", "client", "total_amount", "created_at", "invoices","client_name", "status"
        ]
        read_only_fields = [
            "client_name", "consolidated_invoice_id", "status"
        ]


    def get_client_name(self, obj):
        return obj.client.full_name
    


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'invoice_id', 'amount', 'transaction_code', 'customer_name', 'phone_number', 'date_created'
        ]



