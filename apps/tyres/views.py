from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.tyres.serializers import TyreSerializer
from apps.tyres.services import TyreService
from apps.users.permissions import IsStaffOrAdminOnly
from config.pagination import DefaultPagination
from config.response import error_response, extract_error_message, success_response


class TyreListCreateView(APIView):
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
        queryset = TyreService.list_tyres(filters=filters)
        paginator = DefaultPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        data = [TyreSerializer(item).data for item in page]
        payload = {
            "count": paginator.page.paginator.count,
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "results": data,
        }
        return success_response(payload, message="Tyres fetched successfully")

    def post(self, request):
        serializer = TyreSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(extract_error_message(serializer.errors), status.HTTP_400_BAD_REQUEST)
        tyre = TyreService.create_tyre(serializer.validated_data)
        image_files = request.FILES.getlist("images")
        if image_files:
            TyreService.add_images(tyre, image_files)
        return success_response(TyreSerializer(tyre).data, status.HTTP_201_CREATED, "Tyre created successfully")


class TyreDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_authenticators(self):
        if self.request.method == "GET":
            return []
        return super().get_authenticators()

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated(), IsStaffOrAdminOnly()]

    def get(self, request, tyre_id):
        tyre = TyreService.get_tyre_by_id(tyre_id)
        if not tyre:
            return error_response("Tyre not found", status.HTTP_404_NOT_FOUND)
        return success_response(TyreSerializer(tyre).data, message="Tyre fetched successfully")

    def patch(self, request, tyre_id):
        tyre = TyreService.get_tyre_by_id(tyre_id)
        if not tyre:
            return error_response("Tyre not found", status.HTTP_404_NOT_FOUND)
        serializer = TyreSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response(extract_error_message(serializer.errors), status.HTTP_400_BAD_REQUEST)
        updated = TyreService.update_tyre(tyre, serializer.validated_data)
        return success_response(TyreSerializer(updated).data, message="Tyre updated successfully")

    def delete(self, request, tyre_id):
        tyre = TyreService.get_tyre_by_id(tyre_id)
        if not tyre:
            return error_response("Tyre not found", status.HTTP_404_NOT_FOUND)
        TyreService.delete_tyre(tyre)
        return success_response({"deleted": True}, message="Tyre deleted successfully")


class TyreImagesView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [IsAuthenticated, IsStaffOrAdminOnly]

    def post(self, request, tyre_id):
        tyre = TyreService.get_tyre_by_id(tyre_id)
        if not tyre:
            return error_response("Tyre not found", status.HTTP_404_NOT_FOUND)
        image_files = request.FILES.getlist("images")
        try:
            TyreService.add_images(tyre, image_files)
        except ValueError as exc:
            return error_response(str(exc), status.HTTP_400_BAD_REQUEST)
        return success_response(TyreSerializer(tyre).data, message="Images uploaded successfully")

    def delete(self, request, tyre_id):
        tyre = TyreService.get_tyre_by_id(tyre_id)
        if not tyre:
            return error_response("Tyre not found", status.HTTP_404_NOT_FOUND)
        TyreService.delete_all_images(tyre)
        return success_response(TyreSerializer(tyre).data, message="All images deleted successfully")


class TyreImageDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [IsAuthenticated, IsStaffOrAdminOnly]

    def delete(self, request, image_id):
        try:
            TyreService.delete_image(image_id)
        except ValueError as exc:
            return error_response(str(exc), status.HTTP_404_NOT_FOUND)
        return success_response({"deleted": True}, message="Image deleted successfully")

    def patch(self, request, image_id):
        image_file = request.FILES.get("image")
        if not image_file:
            return error_response("image file is required", status.HTTP_400_BAD_REQUEST)
        try:
            TyreService.update_image(image_id, image_file)
        except ValueError as exc:
            return error_response(str(exc), status.HTTP_404_NOT_FOUND)
        return success_response({"updated": True}, message="Image updated successfully")
