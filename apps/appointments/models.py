"""Appointments models."""

from django.db import models


class Appointment(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        CONFIRMED = "confirmed", "Confirmed"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        NO_SHOW = "no_show", "No Show"

    customer = models.ForeignKey(
        "customers.Customer", on_delete=models.CASCADE, related_name="appointments"
    )
    vehicle = models.ForeignKey(
        "vehicles.Vehicle", on_delete=models.CASCADE, related_name="appointments"
    )
    service_type = models.ForeignKey(
        "services.ServiceType", on_delete=models.PROTECT
    )
    technician = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="appointments",
    )
    scheduled_at = models.DateTimeField()
    estimated_duration_hours = models.DecimalField(max_digits=5, decimal_places=2, default=1)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    notes = models.TextField(blank=True)
    reminder_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["scheduled_at"]

    def __str__(self):
        return f"Appointment #{self.pk} – {self.customer} at {self.scheduled_at}"
