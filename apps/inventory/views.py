from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.inventory.serializers import InventorySerializer, InventoryUpdateSerializer
from apps.inventory.services import InventoryService
from config.response import error_response, extract_error_message, success_response


class InventoryListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = InventoryService.list_inventory()
        return success_response([InventorySerializer(item).data for item in items], message="Inventory fetched successfully")


class InventoryDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, inventory_id):
        role = getattr(request.user, "role", None)
        if role not in {"staff", "admin"}:
            return error_response("Only staff or admin can update inventory", status.HTTP_403_FORBIDDEN)

        item = InventoryService.get_inventory_item(inventory_id)
        if not item:
            return error_response("Inventory item not found", status.HTTP_404_NOT_FOUND)

        serializer = InventoryUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(extract_error_message(serializer.errors), status.HTTP_400_BAD_REQUEST)

        item = InventoryService.update_inventory(item, serializer.validated_data, request.user)
        return success_response(InventorySerializer(item).data, message="Inventory updated successfully")
