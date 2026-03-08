from django.db import models
from infrastructure.database.models import TimestampModel
from common.constants.status_constants import OrderStatus

class Order(TimestampModel):
    order_number = models.CharField(max_length=100, unique=True)
    vehicle = models.ForeignKey('vehicles.Vehicle', on_delete=models.CASCADE, related_name='orders')
    customer = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=OrderStatus.CHOICES, default=OrderStatus.PENDING)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
    
    def __str__(self):
        return self.order_number
