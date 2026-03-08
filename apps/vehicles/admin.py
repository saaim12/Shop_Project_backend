"""Vehicles admin."""

from django.contrib import admin

from .models import Make, Vehicle, VehicleModel


@admin.register(Make)
class MakeAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(VehicleModel)
class VehicleModelAdmin(admin.ModelAdmin):
    list_display = ["make", "name", "year_start", "year_end"]
    list_filter = ["make"]


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ["vin", "year", "make", "model", "customer", "mileage"]
    list_filter = ["make", "year"]
    search_fields = ["vin", "license_plate"]
