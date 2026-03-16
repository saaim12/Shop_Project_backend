from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.rims.serializers import RimSerializer
from apps.rims.services import RimService
from apps.users.permissions import IsStaffOrAdminOnly
from config.pagination import DefaultPagination
from config.response import error_response, extract_error_message, success_response


class RimListCreateView(APIView):
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
            inches = float(request.query_params.get("inches")) if request.query_params.get("inches") else None
        except ValueError:
            return error_response("inches must be numeric", status.HTTP_400_BAD_REQUEST)

        filters = {
            "company": request.query_params.get("company"),
            "condition": (request.query_params.get("condition") or "").upper() or None,
            "inches": inches,
            "type": request.query_params.get("type"),
        }
        queryset = RimService.list_rims(filters=filters)
        paginator = DefaultPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        data = [RimSerializer(item).data for item in page]
        payload = {
            "count": paginator.page.paginator.count,
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "results": data,
        }
        return success_response(payload, message="Rims fetched successfully")

    def post(self, request):
        serializer = RimSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(extract_error_message(serializer.errors), status.HTTP_400_BAD_REQUEST)
        rim = RimService.create_rim(serializer.validated_data)
        image_files = request.FILES.getlist("images")
        if image_files:
            RimService.add_images(rim, image_files)
        return success_response(RimSerializer(rim).data, status.HTTP_201_CREATED, "Rim created successfully")


class RimDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_authenticators(self):
        if self.request.method == "GET":
            return []
        return super().get_authenticators()

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated(), IsStaffOrAdminOnly()]

    def get(self, request, rim_id):
        rim = RimService.get_rim_by_id(rim_id)
        if not rim:
            return error_response("Rim not found", status.HTTP_404_NOT_FOUND)
        return success_response(RimSerializer(rim).data, message="Rim fetched successfully")

    def patch(self, request, rim_id):
        rim = RimService.get_rim_by_id(rim_id)
        if not rim:
            return error_response("Rim not found", status.HTTP_404_NOT_FOUND)
        serializer = RimSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response(extract_error_message(serializer.errors), status.HTTP_400_BAD_REQUEST)
        updated = RimService.update_rim(rim, serializer.validated_data)
        image_files = request.FILES.getlist("images")
        if image_files:
            RimService.delete_all_images(updated)
            try:
                RimService.add_images(updated, image_files)
            except ValueError as exc:
                return error_response(str(exc), status.HTTP_400_BAD_REQUEST)
        return success_response(RimSerializer(updated).data, message="Rim updated successfully")

    def delete(self, request, rim_id):
        rim = RimService.get_rim_by_id(rim_id)
        if not rim:
            return error_response("Rim not found", status.HTTP_404_NOT_FOUND)
        RimService.delete_rim(rim)
        return success_response({"deleted": True}, message="Rim deleted successfully")


class RimImagesView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [IsAuthenticated, IsStaffOrAdminOnly]

    def post(self, request, rim_id):
        rim = RimService.get_rim_by_id(rim_id)
        if not rim:
            return error_response("Rim not found", status.HTTP_404_NOT_FOUND)
        image_files = request.FILES.getlist("images")
        try:
            RimService.add_images(rim, image_files)
        except ValueError as exc:
            return error_response(str(exc), status.HTTP_400_BAD_REQUEST)
        return success_response(RimSerializer(rim).data, message="Images uploaded successfully")

    def delete(self, request, rim_id):
        rim = RimService.get_rim_by_id(rim_id)
        if not rim:
            return error_response("Rim not found", status.HTTP_404_NOT_FOUND)
        RimService.delete_all_images(rim)
        return success_response(RimSerializer(rim).data, message="All images deleted successfully")


class RimImageDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [IsAuthenticated, IsStaffOrAdminOnly]

    def delete(self, request, image_id):
        try:
            RimService.delete_image(image_id)
        except ValueError as exc:
            return error_response(str(exc), status.HTTP_404_NOT_FOUND)
        return success_response({"deleted": True}, message="Image deleted successfully")

    def patch(self, request, image_id):
        image_file = request.FILES.get("image")
        if not image_file:
            return error_response("image file is required", status.HTTP_400_BAD_REQUEST)
        try:
            RimService.update_image(image_id, image_file)
        except ValueError as exc:
            return error_response(str(exc), status.HTTP_404_NOT_FOUND)
        return success_response({"updated": True}, message="Image updated successfully")
