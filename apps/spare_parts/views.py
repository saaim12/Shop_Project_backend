from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.cars.models import Car
from apps.spare_parts.models import SparePart
from apps.spare_parts.serializers import SparePartSerializer
from apps.spare_parts.services import SparePartService
from apps.services.s3_service import UploadFailedError, UploadValidationError
from config.pagination import DefaultPagination
from config.response import error_response, extract_error_message, success_response


class SparePartListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_authenticators(self):
        if self.request.method == "GET":
            return []
        return super().get_authenticators()

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request):
        condition = (request.query_params.get("condition") or "").strip().lower()
        if condition and condition not in {"new", "used", "external"}:
            return error_response("Invalid condition filter", status.HTTP_400_BAD_REQUEST)

        parts = SparePartService.list_spare_parts(condition=condition or None)
        paginator = DefaultPagination()
        paginated_parts = paginator.paginate_queryset(parts, request, view=self)
        data = [SparePartSerializer(part).data for part in paginated_parts]
        payload = {
            "count": paginator.page.paginator.count,
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "results": data,
        }
        return success_response(payload, message="Spare parts fetched successfully")

    def post(self, request):
        role = getattr(request.user, "role", None)
        if role not in {"staff", "admin"}:
            return error_response("Only staff or admin can create spare parts", status.HTTP_403_FORBIDDEN)

        payload = request.data.copy()
        if "images" in payload:
            payload.pop("images")

        serializer = SparePartSerializer(data=payload)
        if not serializer.is_valid():
            return error_response(extract_error_message(serializer.errors), status.HTTP_400_BAD_REQUEST)

        try:
            image_files = request.FILES.getlist("images")
            part = SparePartService.create_spare_part(serializer.validated_data, request.user, image_files=image_files)
        except ValueError as exc:
            return error_response(str(exc), status.HTTP_400_BAD_REQUEST)
        except UploadValidationError as exc:
            return error_response(str(exc), status.HTTP_400_BAD_REQUEST)
        except UploadFailedError as exc:
            return error_response(str(exc), status.HTTP_502_BAD_GATEWAY)

        return success_response(SparePartSerializer(part).data, status.HTTP_201_CREATED, "Spare part created successfully")


class SparePartCreateDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        role = getattr(request.user, "role", None)
        if role not in {"staff", "admin"}:
            return error_response("Only staff or admin can access spare part create data", status.HTTP_403_FORBIDDEN)

        car_options = [
            {
                "id": str(car.id),
                "number_plate": car.number_plate,
                "brand": car.brand,
                "model": car.model,
            }
            for car in Car.objects().order_by("-created_at")
        ]

        payload = {
            "conditions": ["new", "used", "external"],
            "categories": SparePart.CATEGORY_CHOICES,
            "cars": car_options,
            "defaults": {"quantity": 1},
        }
        return success_response(payload, message="Spare part create data fetched successfully")


class SparePartDetailView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_authenticators(self):
        if self.request.method == "GET":
            return []
        return super().get_authenticators()

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, part_id):
        part = SparePartService.get_spare_part_by_id(part_id)
        if not part:
            return error_response("Spare part not found", status.HTTP_404_NOT_FOUND)
        return success_response(SparePartSerializer(part).data, message="Spare part fetched successfully")

    def delete(self, request, part_id):
        part = SparePartService.get_spare_part_by_id(part_id)
        if not part:
            return error_response("Spare part not found", status.HTTP_404_NOT_FOUND)

        role = getattr(request.user, "role", None)
        if role not in {"staff", "admin"}:
            return error_response("Only staff or admin can delete spare parts", status.HTTP_403_FORBIDDEN)

        SparePartService.delete_spare_part(part)
        return success_response({"deleted": True}, message="Spare part deleted successfully")

    def patch(self, request, part_id):
        part = SparePartService.get_spare_part_by_id(part_id)
        if not part:
            return error_response("Spare part not found", status.HTTP_404_NOT_FOUND)

        role = getattr(request.user, "role", None)
        if role not in {"staff", "admin"}:
            return error_response("Only staff or admin can update spare parts", status.HTTP_403_FORBIDDEN)

        # Accept fields from both request body and query params
        body = request.data.dict() if hasattr(request.data, "dict") else dict(request.data)
        payload = {**request.query_params.dict(), **body}
        payload.pop("images", None)
        image_files = request.FILES.getlist("images")

        if not payload and not image_files:
            return error_response("No fields provided to update", status.HTTP_400_BAD_REQUEST)

        if payload:
            serializer = SparePartSerializer(data=payload, partial=True)
            if not serializer.is_valid():
                return error_response(extract_error_message(serializer.errors), status.HTTP_400_BAD_REQUEST)
            validated_payload = serializer.validated_data
        else:
            validated_payload = {}

        try:
            updated_part = SparePartService.update_spare_part(part, validated_payload)
            if image_files:
                updated_part = SparePartService.add_images(updated_part, image_files)
        except ValueError as exc:
            return error_response(str(exc), status.HTTP_400_BAD_REQUEST)
        except UploadValidationError as exc:
            return error_response(str(exc), status.HTTP_400_BAD_REQUEST)
        except UploadFailedError as exc:
            return error_response(str(exc), status.HTTP_502_BAD_GATEWAY)

        return success_response(SparePartSerializer(updated_part).data, message="Spare part updated successfully")


class SparePartImagesView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def _check_staff_or_admin(self, request):
        role = getattr(request.user, "role", None)
        if role not in {"staff", "admin"}:
            return error_response("Only staff or admin can manage spare part images", status.HTTP_403_FORBIDDEN)
        return None

    def post(self, request, part_id):
        """Add new images to a spare part."""
        err = self._check_staff_or_admin(request)
        if err:
            return err

        part = SparePartService.get_spare_part_by_id(part_id)
        if not part:
            return error_response("Spare part not found", status.HTTP_404_NOT_FOUND)

        image_files = request.FILES.getlist("images")
        try:
            updated_part = SparePartService.add_images(part, image_files)
        except ValueError as exc:
            return error_response(str(exc), status.HTTP_400_BAD_REQUEST)
        except UploadValidationError as exc:
            return error_response(str(exc), status.HTTP_400_BAD_REQUEST)
        except UploadFailedError as exc:
            return error_response(str(exc), status.HTTP_502_BAD_GATEWAY)

        return success_response(SparePartSerializer(updated_part).data, message="Images added successfully")

    def delete(self, request, part_id):
        """Delete one image (pass image_url in body) or all images (pass delete_all=true)."""
        err = self._check_staff_or_admin(request)
        if err:
            return err

        part = SparePartService.get_spare_part_by_id(part_id)
        if not part:
            return error_response("Spare part not found", status.HTTP_404_NOT_FOUND)

        delete_all = str(request.data.get("delete_all", "")).lower() in {"true", "1", "yes"}

        if delete_all:
            updated_part = SparePartService.delete_all_images(part)
            return success_response(SparePartSerializer(updated_part).data, message="All images deleted successfully")

        image_url = (request.data.get("image_url") or "").strip()
        if not image_url:
            return error_response("Provide image_url to delete a specific image, or delete_all=true to remove all", status.HTTP_400_BAD_REQUEST)

        try:
            updated_part = SparePartService.delete_image(part, image_url)
        except ValueError as exc:
            return error_response(str(exc), status.HTTP_400_BAD_REQUEST)

        return success_response(SparePartSerializer(updated_part).data, message="Image deleted successfully")
