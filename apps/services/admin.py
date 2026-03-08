"""Services admin."""

from django.contrib import admin

from .models import ServiceCategory, ServiceRecord, ServiceType


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "base_price", "estimated_duration_hours", "is_active"]
    list_filter = ["category", "is_active"]
    search_fields = ["name"]


@admin.register(ServiceRecord)
class ServiceRecordAdmin(admin.ModelAdmin):
    list_display = ["id", "vehicle", "service_type", "technician", "status", "created_at"]
    list_filter = ["status", "service_type"]
    search_fields = ["vehicle__vin"]
