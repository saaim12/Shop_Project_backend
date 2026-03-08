from rest_framework import serializers
from .models import Invoice

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['id', 'invoice_number', 'order', 'amount', 'tax', 'total', 'payment_status', 'due_date', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
