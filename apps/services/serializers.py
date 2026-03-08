"""Services serializers."""

from rest_framework import serializers

from .models import ServiceCategory, ServiceRecord, ServiceType


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ["id", "name", "description"]


class ServiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceType
        fields = [
            "id",
            "category",
            "name",
            "description",
            "estimated_duration_hours",
            "base_price",
            "is_active",
        ]


class ServiceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRecord
        fields = [
            "id",
            "vehicle",
            "service_type",
            "technician",
            "status",
            "description",
            "labor_cost",
            "started_at",
            "completed_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
