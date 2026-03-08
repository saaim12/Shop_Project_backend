"""Vehicles views."""

from rest_framework import viewsets

from .models import Make, Vehicle, VehicleModel
from .serializers import MakeSerializer, VehicleModelSerializer, VehicleSerializer


class MakeViewSet(viewsets.ModelViewSet):
    queryset = Make.objects.all()
    serializer_class = MakeSerializer
    search_fields = ["name"]


class VehicleModelViewSet(viewsets.ModelViewSet):
    queryset = VehicleModel.objects.select_related("make").all()
    serializer_class = VehicleModelSerializer
    filterset_fields = ["make"]


class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.select_related("customer", "make", "model").all()
    serializer_class = VehicleSerializer
    filterset_fields = ["customer", "make", "year"]
    search_fields = ["vin", "license_plate"]
