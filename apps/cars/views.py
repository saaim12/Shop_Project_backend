from datetime import datetime, timezone

from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.cars.serializers import CarSerializer
from apps.cars.services import CarService
from apps.users.permissions import IsStaffOrAdminOnly
from config.pagination import DefaultPagination
from config.response import error_response, extract_error_message, success_response


def _parse_iso_datetime(value, field_name):
    if value in (None, ""):
        return None

    normalized_value = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized_value)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a valid ISO datetime") from exc

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


class CarListCreateView(APIView):
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
            year = int(request.query_params.get("year")) if request.query_params.get("year") else None
            created_at = _parse_iso_datetime(request.query_params.get("created_at"), "created_at")
            created_at_from = _parse_iso_datetime(request.query_params.get("created_at_from"), "created_at_from")
            created_at_to = _parse_iso_datetime(request.query_params.get("created_at_to"), "created_at_to")
        except ValueError:
            return error_response("model_year and year must be integers, and created_at fields must be valid ISO datetime", status.HTTP_400_BAD_REQUEST)

        filters = {
            "name": request.query_params.get("name"),
            "brand": request.query_params.get("brand"),
            "model": request.query_params.get("model"),
            "model_year": model_year,
            "year": year,
            "condition": (request.query_params.get("condition") or "").upper() or None,
            "chassis_number": request.query_params.get("chassis_number"),
            "created_at": created_at,
            "created_at__gte": created_at_from,
            "created_at__lte": created_at_to,
        }
        queryset = CarService.list_cars(filters=filters)
        paginator = DefaultPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        data = [CarSerializer(car).data for car in page]
        payload = {
            "count": paginator.page.paginator.count,
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "results": data,
        }
        return success_response(payload, message="Cars fetched successfully")

    def post(self, request):
        serializer = CarSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(extract_error_message(serializer.errors), status.HTTP_400_BAD_REQUEST)
        try:
            car = CarService.create_car(serializer.validated_data)
        except ValueError as exc:
            return error_response(str(exc), status.HTTP_400_BAD_REQUEST)
        image_files = request.FILES.getlist("images")
        if image_files:
            CarService.add_images(car, image_files)
        return success_response(CarSerializer(car).data, status.HTTP_201_CREATED, "Car created successfully")


class CarDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_authenticators(self):
        if self.request.method == "GET":
            return []
        return super().get_authenticators()

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated(), IsStaffOrAdminOnly()]

    def get(self, request, car_id):
        car = CarService.get_car_by_id(car_id)
        if not car:
            return error_response("Car not found", status.HTTP_404_NOT_FOUND)
        return success_response(CarSerializer(car).data, message="Car fetched successfully")

    def patch(self, request, car_id):
        car = CarService.get_car_by_id(car_id)
        if not car:
            return error_response("Car not found", status.HTTP_404_NOT_FOUND)
        serializer = CarSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response(extract_error_message(serializer.errors), status.HTTP_400_BAD_REQUEST)
        try:
            updated = CarService.update_car(car, serializer.validated_data)
        except ValueError as exc:
            return error_response(str(exc), status.HTTP_400_BAD_REQUEST)
        image_files = request.FILES.getlist("images")
        if image_files:
            CarService.delete_all_images(updated)
            try:
                CarService.add_images(updated, image_files)
            except ValueError as exc:
                return error_response(str(exc), status.HTTP_400_BAD_REQUEST)
        return success_response(CarSerializer(updated).data, message="Car updated successfully")

    def delete(self, request, car_id):
        car = CarService.get_car_by_id(car_id)
        if not car:
            return error_response("Car not found", status.HTTP_404_NOT_FOUND)
        CarService.delete_car(car)
        return success_response({"deleted": True}, message="Car deleted successfully")


class CarImagesView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [IsAuthenticated, IsStaffOrAdminOnly]

    def post(self, request, car_id):
        car = CarService.get_car_by_id(car_id)
        if not car:
            return error_response("Car not found", status.HTTP_404_NOT_FOUND)
        image_files = request.FILES.getlist("images")
        try:
            CarService.add_images(car, image_files)
        except ValueError as exc:
            return error_response(str(exc), status.HTTP_400_BAD_REQUEST)
        return success_response(CarSerializer(car).data, message="Images uploaded successfully")

    def delete(self, request, car_id):
        car = CarService.get_car_by_id(car_id)
        if not car:
            return error_response("Car not found", status.HTTP_404_NOT_FOUND)
        CarService.delete_all_images(car)
        return success_response(CarSerializer(car).data, message="All images deleted successfully")


class CarImageDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [IsAuthenticated, IsStaffOrAdminOnly]

    def delete(self, request, image_id):
        try:
            CarService.delete_image(image_id)
        except ValueError as exc:
            return error_response(str(exc), status.HTTP_404_NOT_FOUND)
        return success_response({"deleted": True}, message="Image deleted successfully")

    def patch(self, request, image_id):
        image_file = request.FILES.get("image")
        if not image_file:
            return error_response("image file is required", status.HTTP_400_BAD_REQUEST)
        try:
            CarService.update_image(image_id, image_file)
        except ValueError as exc:
            return error_response(str(exc), status.HTTP_404_NOT_FOUND)
        return success_response({"updated": True}, message="Image updated successfully")
