"""Parts views."""

from django.db import models
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Part, PartCategory, StockAdjustment
from .serializers import PartCategorySerializer, PartSerializer, StockAdjustmentSerializer


class PartCategoryViewSet(viewsets.ModelViewSet):
    queryset = PartCategory.objects.all()
    serializer_class = PartCategorySerializer
    search_fields = ["name"]


class PartViewSet(viewsets.ModelViewSet):
    queryset = Part.objects.select_related("category", "supplier").all()
    serializer_class = PartSerializer
    filterset_fields = ["category", "supplier", "is_active"]
    search_fields = ["name", "part_number"]

    @action(detail=False, methods=["get"], url_path="low-stock")
    def low_stock(self, request):
        low = self.get_queryset().filter(
            quantity_in_stock__lte=models.F("reorder_level")
        )
        serializer = self.get_serializer(low, many=True)
        return Response(serializer.data)


class StockAdjustmentViewSet(viewsets.ModelViewSet):
    queryset = StockAdjustment.objects.select_related("part").all()
    serializer_class = StockAdjustmentSerializer
    filterset_fields = ["part", "adjustment_type"]
    http_method_names = ["get", "post", "head", "options"]
