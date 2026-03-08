"""Employees admin."""

from django.contrib import admin

from .models import Department, Employee


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ["user", "department", "position", "status", "hire_date"]
    list_filter = ["department", "status"]
    search_fields = ["user__first_name", "user__last_name", "position"]
