from rest_framework import serializers
from .models import Order

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'order_number', 'vehicle', 'customer', 'status', 'total_amount', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
