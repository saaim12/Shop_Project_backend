from django.db import models
from infrastructure.database.models import TimestampModel
from common.constants.status_constants import VehicleType, FuelType

class Vehicle(TimestampModel):
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    vin = models.CharField(max_length=17, unique=True)
    license_plate = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(max_length=20, choices=VehicleType.CHOICES)
    fuel_type = models.CharField(max_length=20, choices=FuelType.CHOICES)
    mileage = models.IntegerField(default=0)
    color = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Vehicle'
        verbose_name_plural = 'Vehicles'
    
    def __str__(self):
        return f"{self.year} {self.make} {self.model}"
