"""Services URL configuration."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ServiceCategoryViewSet, ServiceRecordViewSet, ServiceTypeViewSet

router = DefaultRouter()
router.register("categories", ServiceCategoryViewSet, basename="service-category")
router.register("types", ServiceTypeViewSet, basename="service-type")
router.register("records", ServiceRecordViewSet, basename="service-record")

urlpatterns = [path("", include(router.urls))]
