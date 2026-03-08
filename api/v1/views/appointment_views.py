from django.urls import path
from rest_framework.routers import DefaultRouter
from apps.appointments.serializers import AppointmentSerializer
from rest_framework.viewsets import ModelViewSet
from apps.appointments.models import Appointment

class AppointmentViewSet(ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

router = DefaultRouter()
router.register(r'', AppointmentViewSet, basename='appointment')

urlpatterns = router.urls
