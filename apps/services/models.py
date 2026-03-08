"""Services models."""

from django.db import models


class ServiceCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Service Categories"

    def __str__(self):
        return self.name


class ServiceType(models.Model):
    category = models.ForeignKey(
        ServiceCategory, on_delete=models.CASCADE, related_name="service_types"
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    estimated_duration_hours = models.DecimalField(max_digits=5, decimal_places=2, default=1)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.category} – {self.name}"


class ServiceRecord(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    vehicle = models.ForeignKey(
        "vehicles.Vehicle", on_delete=models.CASCADE, related_name="service_records"
    )
    service_type = models.ForeignKey(ServiceType, on_delete=models.PROTECT)
    technician = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_services",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    description = models.TextField(blank=True)
    labor_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ServiceRecord #{self.pk} – {self.service_type} ({self.status})"
