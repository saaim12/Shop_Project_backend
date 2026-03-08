"""Orders URL configuration."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import OrderItemViewSet, OrderViewSet

router = DefaultRouter()
router.register("items", OrderItemViewSet, basename="order-item")
router.register("", OrderViewSet, basename="order")

urlpatterns = [path("", include(router.urls))]
