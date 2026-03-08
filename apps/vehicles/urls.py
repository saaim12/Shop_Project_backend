"""Vehicles URL configuration."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MakeViewSet, VehicleModelViewSet, VehicleViewSet

router = DefaultRouter()
router.register("makes", MakeViewSet, basename="make")
router.register("vehicle-models", VehicleModelViewSet, basename="vehicle-model")
router.register("", VehicleViewSet, basename="vehicle")

urlpatterns = [path("", include(router.urls))]
