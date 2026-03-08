"""Appointments serializers."""

from rest_framework import serializers

from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = [
            "id",
            "customer",
            "vehicle",
            "service_type",
            "technician",
            "scheduled_at",
            "estimated_duration_hours",
            "status",
            "notes",
            "reminder_sent",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "reminder_sent", "created_at", "updated_at"]
