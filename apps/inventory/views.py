from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.inventory.serializers import InventorySerializer
from apps.inventory.services import InventoryService
from apps.users.permissions import IsAdmin, IsStaffOrAdminOnly
from config.pagination import DefaultPagination
from config.response import error_response, extract_error_message, success_response


class InventoryListCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_permissions(self):
        if self.request.method in {"GET", "POST"}:
            return [IsAuthenticated(), IsStaffOrAdminOnly()]
        return [IsAuthenticated(), IsAdmin()]

    def get(self, request):
        try:
            queryset = InventoryService.list_inventory(
                category=request.query_params.get("category"),
                stored_by_id=request.query_params.get("stored_by") or request.query_params.get("user_id"),
            )
        except ValueError as exc:
            return error_response(str(exc), status.HTTP_400_BAD_REQUEST)

        paginator = DefaultPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        data = [InventorySerializer(item).data for item in page]

        payload = {
            "count": paginator.page.paginator.count,
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "results": data,
        }
        return success_response(payload, message="Inventory fetched successfully")

    def post(self, request):
        serializer = InventorySerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(extract_error_message(serializer.errors), status.HTTP_400_BAD_REQUEST)

        try:
            item = InventoryService.create_inventory(serializer.validated_data, request.user)
        except ValueError as exc:
            return error_response(str(exc), status.HTTP_400_BAD_REQUEST)

        if item is None:
            return success_response({"deleted": True}, message="Inventory entry removed because quantity is 0")

        return success_response(InventorySerializer(item).data, status.HTTP_201_CREATED, "Inventory created successfully")


class InventoryDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_permissions(self):
        if self.request.method in {"PATCH", "DELETE"}:
            return [IsAuthenticated(), IsStaffOrAdminOnly()]
        return [IsAuthenticated(), IsAdmin()]

    def patch(self, request, inventory_id):
        item = InventoryService.get_inventory_item(inventory_id)
        if not item:
            return error_response("Inventory item not found", status.HTTP_404_NOT_FOUND)

        serializer = InventorySerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response(extract_error_message(serializer.errors), status.HTTP_400_BAD_REQUEST)

        try:
            updated_item = InventoryService.update_inventory(item, serializer.validated_data, request.user)
        except ValueError as exc:
            return error_response(str(exc), status.HTTP_400_BAD_REQUEST)

        if updated_item is None:
            return success_response({"deleted": True}, message="Inventory entry removed because quantity is 0")

        return success_response(InventorySerializer(updated_item).data, message="Inventory updated successfully")

    def delete(self, request, inventory_id):
        item = InventoryService.get_inventory_item(inventory_id)
        if not item:
            return error_response("Inventory item not found", status.HTTP_404_NOT_FOUND)
        try:
            InventoryService.delete_inventory(item)
        except ValueError as exc:
            return error_response(str(exc), status.HTTP_400_BAD_REQUEST)
        return success_response({"deleted": True}, message="Inventory deleted successfully")
