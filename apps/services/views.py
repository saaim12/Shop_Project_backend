"""Services views."""

from rest_framework import viewsets

from .models import ServiceCategory, ServiceRecord, ServiceType
from .serializers import ServiceCategorySerializer, ServiceRecordSerializer, ServiceTypeSerializer


class ServiceCategoryViewSet(viewsets.ModelViewSet):
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer
    search_fields = ["name"]


class ServiceTypeViewSet(viewsets.ModelViewSet):
    queryset = ServiceType.objects.select_related("category").all()
    serializer_class = ServiceTypeSerializer
    filterset_fields = ["category", "is_active"]
    search_fields = ["name"]


class ServiceRecordViewSet(viewsets.ModelViewSet):
    queryset = ServiceRecord.objects.select_related(
        "vehicle", "service_type", "technician"
    ).all()
    serializer_class = ServiceRecordSerializer
    filterset_fields = ["vehicle", "status", "technician"]
    ordering_fields = ["created_at", "completed_at"]
