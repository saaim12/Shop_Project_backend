"""Invoices serializers."""

from rest_framework import serializers

from .models import Invoice


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            "id",
            "order",
            "invoice_number",
            "status",
            "subtotal",
            "tax_rate",
            "tax_amount",
            "discount_amount",
            "total_amount",
            "payment_method",
            "paid_at",
            "due_date",
            "notes",
            "issued_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
