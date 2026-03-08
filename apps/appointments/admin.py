"""Appointments admin."""

from django.contrib import admin

from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "customer",
        "vehicle",
        "service_type",
        "technician",
        "scheduled_at",
        "status",
    ]
    list_filter = ["status", "scheduled_at"]
    search_fields = ["customer__first_name", "customer__last_name", "vehicle__vin"]
