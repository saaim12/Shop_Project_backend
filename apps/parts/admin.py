"""Parts admin."""

from django.contrib import admin

from .models import Part, PartCategory, StockAdjustment


@admin.register(PartCategory)
class PartCategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = [
        "part_number",
        "name",
        "category",
        "quantity_in_stock",
        "reorder_level",
        "selling_price",
        "is_active",
    ]
    list_filter = ["category", "is_active"]
    search_fields = ["part_number", "name"]


@admin.register(StockAdjustment)
class StockAdjustmentAdmin(admin.ModelAdmin):
    list_display = ["part", "adjustment_type", "quantity", "created_at"]
    list_filter = ["adjustment_type"]
