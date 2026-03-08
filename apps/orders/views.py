"""Orders views."""

from rest_framework import viewsets

from .models import Order, OrderItem
from .serializers import OrderItemSerializer, OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related("items").select_related(
        "customer", "vehicle", "appointment"
    ).all()
    serializer_class = OrderSerializer
    filterset_fields = ["customer", "vehicle", "status"]
    search_fields = ["customer__first_name", "customer__last_name", "vehicle__vin"]
    ordering_fields = ["created_at", "updated_at"]


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.select_related("order", "part", "service_record").all()
    serializer_class = OrderItemSerializer
    filterset_fields = ["order", "item_type"]
