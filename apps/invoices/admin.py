"""Invoices admin."""

from django.contrib import admin

from .models import Invoice


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        "invoice_number",
        "order",
        "status",
        "total_amount",
        "payment_method",
        "due_date",
        "paid_at",
    ]
    list_filter = ["status", "payment_method"]
    search_fields = ["invoice_number", "order__customer__first_name", "order__customer__last_name"]
    readonly_fields = ["created_at", "updated_at"]
