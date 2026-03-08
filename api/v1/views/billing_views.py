from django.urls import path
from rest_framework.routers import DefaultRouter
from apps.billing.serializers import InvoiceSerializer
from rest_framework.viewsets import ModelViewSet
from apps.billing.models import Invoice

class InvoiceViewSet(ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

router = DefaultRouter()
router.register(r'', InvoiceViewSet, basename='invoice')

urlpatterns = router.urls
