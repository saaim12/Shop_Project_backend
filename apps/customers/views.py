"""Customers views."""

from rest_framework import viewsets

from .models import Customer
from .serializers import CustomerSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    filterset_fields = ["city", "state"]
    search_fields = ["first_name", "last_name", "email", "phone"]
    ordering_fields = ["last_name", "created_at"]
