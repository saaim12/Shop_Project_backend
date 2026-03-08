from django.urls import path
from rest_framework.routers import DefaultRouter
from apps.vehicles.serializers import VehicleSerializer
from rest_framework.viewsets import ModelViewSet
from apps.vehicles.models import Vehicle

class VehicleViewSet(ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer

router = DefaultRouter()
router.register(r'', VehicleViewSet, basename='vehicle')

urlpatterns = router.urls
