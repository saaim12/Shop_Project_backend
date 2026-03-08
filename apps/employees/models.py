"""Employees models."""

from django.conf import settings
from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Employee(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        ON_LEAVE = "on_leave", "On Leave"
        TERMINATED = "terminated", "Terminated"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employee_profile",
    )
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, related_name="employees"
    )
    position = models.CharField(max_length=100)
    hire_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    certifications = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} – {self.position}"
