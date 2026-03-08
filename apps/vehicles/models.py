"""Vehicles models."""

from django.db import models


class Make(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class VehicleModel(models.Model):
    make = models.ForeignKey(Make, on_delete=models.CASCADE, related_name="models")
    name = models.CharField(max_length=100)
    year_start = models.PositiveSmallIntegerField()
    year_end = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ("make", "name", "year_start")

    def __str__(self):
        return f"{self.make} {self.name} ({self.year_start})"


class Vehicle(models.Model):
    customer = models.ForeignKey(
        "customers.Customer", on_delete=models.CASCADE, related_name="vehicles"
    )
    make = models.ForeignKey(Make, on_delete=models.SET_NULL, null=True)
    model = models.ForeignKey(VehicleModel, on_delete=models.SET_NULL, null=True)
    year = models.PositiveSmallIntegerField()
    vin = models.CharField(max_length=17, unique=True)
    license_plate = models.CharField(max_length=20, blank=True)
    color = models.CharField(max_length=50, blank=True)
    mileage = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.year} {self.make} {self.model} – {self.vin}"
