from django.db import models
from infrastructure.database.models import TimestampModel

class User(TimestampModel):
    USER_TYPES = [
        ('customer', 'Customer'),
        ('mechanic', 'Mechanic'),
        ('manager', 'Manager'),
        ('admin', 'Admin'),
    ]
    
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='customer')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
