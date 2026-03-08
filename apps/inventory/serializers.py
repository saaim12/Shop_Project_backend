from rest_framework import serializers
from .models import Part

class PartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Part
        fields = ['id', 'name', 'part_number', 'description', 'quantity_in_stock', 'reorder_level', 'price', 'supplier', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
