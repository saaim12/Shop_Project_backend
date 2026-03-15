from django.urls import path

from apps.inventory.views import InventoryDetailView, InventoryListCreateView


urlpatterns = [
    path("", InventoryListCreateView.as_view(), name="inventory-list-create"),
    path("<str:inventory_id>", InventoryDetailView.as_view(), name="inventory-detail"),
]
