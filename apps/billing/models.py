from django.db import models
from infrastructure.database.models import TimestampModel
from common.constants.status_constants import PaymentStatus

class Invoice(TimestampModel):
    invoice_number = models.CharField(max_length=100, unique=True)
    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='invoice')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.CHOICES, default=PaymentStatus.PENDING)
    due_date = models.DateField()
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
    
    def __str__(self):
        return self.invoice_number
