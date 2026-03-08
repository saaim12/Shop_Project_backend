from rest_framework import serializers
from .models import Vehicle

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['id', 'make', 'model', 'year', 'vin', 'license_plate', 'vehicle_type', 'fuel_type', 'mileage', 'color', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
