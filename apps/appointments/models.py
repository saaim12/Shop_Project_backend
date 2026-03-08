from django.db import models
from infrastructure.database.models import TimestampModel
from common.constants.status_constants import AppointmentStatus

class Appointment(TimestampModel):
    vehicle = models.ForeignKey('vehicles.Vehicle', on_delete=models.CASCADE, related_name='appointments')
    customer = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='appointments')
    service = models.ForeignKey('services.Service', on_delete=models.SET_NULL, null=True, related_name='appointments')
    appointment_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=AppointmentStatus.CHOICES, default=AppointmentStatus.PENDING)
    mechanic = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_appointments')
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-appointment_date']
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'
    
    def __str__(self):
        return f"{self.customer} - {self.appointment_date}"
