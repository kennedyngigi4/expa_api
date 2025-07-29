from rest_framework import serializers
from apps.payments.models import *


class InvoiceSerializer(serializers.ModelSerializer):

    package_name = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = [
            'id', "invoice_id", "package", "package_name", "amount", "status", "issued_at"
        ]

    def get_package_name(self, obj):
        return obj.package.package_id

