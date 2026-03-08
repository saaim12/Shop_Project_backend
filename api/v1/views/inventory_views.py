from django.urls import path
from rest_framework.routers import DefaultRouter
from apps.inventory.serializers import PartSerializer
from rest_framework.viewsets import ModelViewSet
from apps.inventory.models import Part

class PartViewSet(ModelViewSet):
    queryset = Part.objects.all()
    serializer_class = PartSerializer

router = DefaultRouter()
router.register(r'', PartViewSet, basename='part')

urlpatterns = router.urls
