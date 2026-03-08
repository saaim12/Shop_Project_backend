from django.urls import path
from rest_framework.routers import DefaultRouter
from apps.services.serializers import ServiceSerializer
from rest_framework.viewsets import ModelViewSet
from apps.services.models import Service

class ServiceViewSet(ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

router = DefaultRouter()
router.register(r'', ServiceViewSet, basename='service')

urlpatterns = router.urls
