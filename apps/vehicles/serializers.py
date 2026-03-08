"""Vehicles serializers."""

from rest_framework import serializers

from .models import Make, Vehicle, VehicleModel


class MakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Make
        fields = ["id", "name"]


class VehicleModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleModel
        fields = ["id", "make", "name", "year_start", "year_end"]


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = [
            "id",
            "customer",
            "make",
            "model",
            "year",
            "vin",
            "license_plate",
            "color",
            "mileage",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
