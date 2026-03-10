from django.urls import path

from apps.inventory.views import InventoryDetailView, InventoryListView


urlpatterns = [
    path("", InventoryListView.as_view(), name="inventory-list"),
    path("<str:inventory_id>/", InventoryDetailView.as_view(), name="inventory-detail"),
]
