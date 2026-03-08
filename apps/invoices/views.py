"""Invoices views."""

from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Invoice
from .serializers import InvoiceSerializer


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.select_related("order__customer").all()
    serializer_class = InvoiceSerializer
    filterset_fields = ["status", "payment_method"]
    search_fields = ["invoice_number", "order__customer__first_name", "order__customer__last_name"]
    ordering_fields = ["created_at", "due_date", "total_amount"]

    @action(detail=True, methods=["post"], url_path="mark-paid")
    def mark_paid(self, request, pk=None):
        invoice = self.get_object()
        invoice.status = Invoice.Status.PAID
        invoice.paid_at = timezone.now()
        invoice.payment_method = request.data.get("payment_method", Invoice.PaymentMethod.CASH)
        invoice.save()
        return Response(self.get_serializer(invoice).data)
