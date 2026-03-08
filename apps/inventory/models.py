from django.db import models
from infrastructure.database.models import TimestampModel

class Part(TimestampModel):
    name = models.CharField(max_length=200)
    part_number = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    quantity_in_stock = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=10)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    supplier = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Part'
        verbose_name_plural = 'Parts'
    
    def __str__(self):
        return self.name
