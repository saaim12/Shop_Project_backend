"""Orders serializers."""

from rest_framework import serializers

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "order",
            "item_type",
            "part",
            "service_record",
            "quantity",
            "unit_price",
            "subtotal",
        ]
        read_only_fields = ["id", "subtotal"]


class OrderSerializer(serializers.ModelSerializer):
    total_amount = serializers.ReadOnlyField()
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "customer",
            "vehicle",
            "appointment",
            "status",
            "notes",
            "total_amount",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "total_amount", "created_at", "updated_at"]
