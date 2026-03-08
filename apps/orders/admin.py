"""Orders admin."""

from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["subtotal"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "customer", "vehicle", "status", "total_amount", "created_at"]
    list_filter = ["status"]
    search_fields = ["customer__first_name", "customer__last_name", "vehicle__vin"]
    inlines = [OrderItemInline]
    readonly_fields = ["total_amount"]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["id", "order", "item_type", "quantity", "unit_price", "subtotal"]
    list_filter = ["item_type"]
