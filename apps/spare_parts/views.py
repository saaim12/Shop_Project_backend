from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.spare_parts.serializers import SparePartSerializer
from apps.spare_parts.services import SparePartService
from apps.users.permissions import IsStaffOrAdminOnly
from config.pagination import DefaultPagination
from config.response import error_response, extract_error_message, success_response


class SparePartListCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_authenticators(self):
        if self.request.method == "GET":
            return []
        return super().get_authenticators()

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated(), IsStaffOrAdminOnly()]

    def get(self, request):
        try:
            model_year = int(request.query_params.get("model_year")) if request.query_params.get("model_year") else None
        except ValueError:
            return error_response("model_year must be an integer", status.HTTP_400_BAD_REQUEST)

        filters = {
            "name": request.query_params.get("name"),
            "brand": request.query_params.get("brand"),
            "model": request.query_params.get("model"),
            "model_year": model_year,
            "vehicle_type": request.query_params.get("vehicle_type"),
            "category": request.query_params.get("category"),
            "condition": (request.query_params.get("condition") or "").upper() or None,
            "item_number": request.query_params.get("item_number"),
            "engine_code": request.query_params.get("engine_code"),
            "oem_numbers": request.query_params.get("oem_numbers"),
        }
        queryset = SparePartService.list_spare_parts(filters=filters)
        paginator = DefaultPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        data = [SparePartSerializer(part).data for part in page]
        payload = {
            "count": paginator.page.paginator.count,
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "results": data,
        }
        return success_response(payload, message="Spare parts fetched successfully")

    def post(self, request):
        serializer = SparePartSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(extract_error_message(serializer.errors), status.HTTP_400_BAD_REQUEST)
        part = SparePartService.create_spare_part(serializer.validated_data)
        image_files = request.FILES.getlist("images")
        if image_files:
            SparePartService.add_images(part, image_files)
        return success_response(SparePartSerializer(part).data, status.HTTP_201_CREATED, "Spare part created successfully")


class SparePartDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_authenticators(self):
        if self.request.method == "GET":
            return []
        return super().get_authenticators()

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated(), IsStaffOrAdminOnly()]

    def get(self, request, part_id):
        part = SparePartService.get_spare_part_by_id(part_id)
        if not part:
            return error_response("Spare part not found", status.HTTP_404_NOT_FOUND)
        return success_response(SparePartSerializer(part).data, message="Spare part fetched successfully")

    def patch(self, request, part_id):
        part = SparePartService.get_spare_part_by_id(part_id)
        if not part:
            return error_response("Spare part not found", status.HTTP_404_NOT_FOUND)
        serializer = SparePartSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response(extract_error_message(serializer.errors), status.HTTP_400_BAD_REQUEST)
        updated = SparePartService.update_spare_part(part, serializer.validated_data)
        return success_response(SparePartSerializer(updated).data, message="Spare part updated successfully")

    def delete(self, request, part_id):
        part = SparePartService.get_spare_part_by_id(part_id)
        if not part:
            return error_response("Spare part not found", status.HTTP_404_NOT_FOUND)
        SparePartService.delete_spare_part(part)
        return success_response({"deleted": True}, message="Spare part deleted successfully")


class SparePartImagesView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [IsAuthenticated, IsStaffOrAdminOnly]

    def post(self, request, part_id):
        part = SparePartService.get_spare_part_by_id(part_id)
        if not part:
            return error_response("Spare part not found", status.HTTP_404_NOT_FOUND)
        image_files = request.FILES.getlist("images")
        try:
            SparePartService.add_images(part, image_files)
        except ValueError as exc:
            return error_response(str(exc), status.HTTP_400_BAD_REQUEST)
        return success_response(SparePartSerializer(part).data, message="Images uploaded successfully")

    def delete(self, request, part_id):
        part = SparePartService.get_spare_part_by_id(part_id)
        if not part:
            return error_response("Spare part not found", status.HTTP_404_NOT_FOUND)
        SparePartService.delete_all_images(part)
        return success_response(SparePartSerializer(part).data, message="All images deleted successfully")


class SparePartImageDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [IsAuthenticated, IsStaffOrAdminOnly]

    def delete(self, request, image_id):
        try:
            SparePartService.delete_image(image_id)
        except ValueError as exc:
            return error_response(str(exc), status.HTTP_404_NOT_FOUND)
        return success_response({"deleted": True}, message="Image deleted successfully")

    def patch(self, request, image_id):
        image_file = request.FILES.get("image")
        if not image_file:
            return error_response("image file is required", status.HTTP_400_BAD_REQUEST)
        try:
            SparePartService.update_image(image_id, image_file)
        except ValueError as exc:
            return error_response(str(exc), status.HTTP_404_NOT_FOUND)
        return success_response({"updated": True}, message="Image updated successfully")
