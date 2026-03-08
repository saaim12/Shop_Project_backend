from rest_framework import serializers
from .models import Appointment

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['id', 'vehicle', 'customer', 'service', 'appointment_date', 'status', 'mechanic', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
