"""Parts URL configuration."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PartCategoryViewSet, PartViewSet, StockAdjustmentViewSet

router = DefaultRouter()
router.register("categories", PartCategoryViewSet, basename="part-category")
router.register("stock-adjustments", StockAdjustmentViewSet, basename="stock-adjustment")
router.register("", PartViewSet, basename="part")

urlpatterns = [path("", include(router.urls))]
