"""Appointments views."""

from rest_framework import viewsets

from .models import Appointment
from .serializers import AppointmentSerializer


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.select_related(
        "customer", "vehicle", "service_type", "technician"
    ).all()
    serializer_class = AppointmentSerializer
    filterset_fields = ["customer", "vehicle", "technician", "status"]
    search_fields = ["customer__first_name", "customer__last_name", "vehicle__vin"]
    ordering_fields = ["scheduled_at", "created_at"]
