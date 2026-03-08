from django.urls import path
from rest_framework.routers import DefaultRouter
from apps.orders.serializers import OrderSerializer
from rest_framework.viewsets import ModelViewSet
from apps.orders.models import Order

class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

router = DefaultRouter()
router.register(r'', OrderViewSet, basename='order')

urlpatterns = router.urls
