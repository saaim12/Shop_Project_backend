"""Parts serializers."""

from rest_framework import serializers

from .models import Part, PartCategory, StockAdjustment


class PartCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PartCategory
        fields = ["id", "name", "description"]


class PartSerializer(serializers.ModelSerializer):
    is_low_stock = serializers.ReadOnlyField()

    class Meta:
        model = Part
        fields = [
            "id",
            "category",
            "supplier",
            "name",
            "part_number",
            "description",
            "unit_cost",
            "selling_price",
            "quantity_in_stock",
            "reorder_level",
            "location",
            "image",
            "is_active",
            "is_low_stock",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "is_low_stock", "created_at", "updated_at"]


class StockAdjustmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockAdjustment
        fields = ["id", "part", "adjustment_type", "quantity", "notes", "created_at"]
        read_only_fields = ["id", "created_at"]
