from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.cars.serializers import CarSerializer
from apps.cars.services import CarService
from apps.services.s3_service import UploadFailedError, UploadValidationError
from config.pagination import DefaultPagination
from config.response import error_response, extract_error_message, success_response


class CarListView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        cars = CarService.list_cars()
        paginator = DefaultPagination()
        paginated_cars = paginator.paginate_queryset(cars, request, view=self)
        data = [CarSerializer(car).data for car in paginated_cars]
        payload = {
            "count": paginator.page.paginator.count,
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "results": data,
        }
        return success_response(payload, message="Cars fetched successfully")


class CarCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        role = getattr(request.user, "role", None)
        if role not in {"staff", "admin"}:
            return error_response("Only staff or admin can create cars", status.HTTP_403_FORBIDDEN)

        payload = request.data.copy()
        if "images" in payload:
            payload.pop("images")

        serializer = CarSerializer(data=payload)
        if not serializer.is_valid():
            return error_response(extract_error_message(serializer.errors), status.HTTP_400_BAD_REQUEST)

        try:
            car = CarService.create_car(serializer.validated_data, request.user)
            image_files = request.FILES.getlist("images")
            if image_files:
                car = CarService.add_images(car, image_files)
        except ValueError as exc:
            return error_response(str(exc), status.HTTP_400_BAD_REQUEST)
        except UploadValidationError as exc:
            return error_response(str(exc), status.HTTP_400_BAD_REQUEST)
        except UploadFailedError as exc:
            return error_response(str(exc), status.HTTP_502_BAD_GATEWAY)

        return success_response(CarSerializer(car).data, status.HTTP_201_CREATED, "Car created successfully")


class CarDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_authenticators(self):
        if self.request.method == "GET":
            return []
        return super().get_authenticators()

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, car_id):
        car = CarService.get_car_by_id(car_id)
        if not car:
            return error_response("Car not found", status.HTTP_404_NOT_FOUND)
        return success_response(CarSerializer(car).data, message="Car fetched successfully")

    def delete(self, request, car_id):
        car = CarService.get_car_by_id(car_id)
        if not car:
            return error_response("Car not found", status.HTTP_404_NOT_FOUND)

        role = getattr(request.user, "role", None)
        if role not in {"staff", "admin"}:
            return error_response("Only staff or admin can delete cars", status.HTTP_403_FORBIDDEN)

        CarService.delete_car(car)
        return success_response({"deleted": True}, message="Car deleted successfully")

    def patch(self, request, car_id):
        car = CarService.get_car_by_id(car_id)
        if not car:
            return error_response("Car not found", status.HTTP_404_NOT_FOUND)

        role = getattr(request.user, "role", None)
        if role not in {"staff", "admin"}:
            return error_response("Only staff or admin can update cars", status.HTTP_403_FORBIDDEN)

        payload = request.data.dict() if hasattr(request.data, "dict") else dict(request.data)
        payload.pop("images", None)

        serializer = CarSerializer(data=payload, partial=True, context={"car_id": car_id})
        if not serializer.is_valid():
            return error_response(extract_error_message(serializer.errors), status.HTTP_400_BAD_REQUEST)

        try:
            updated_car = CarService.update_car(car, serializer.validated_data)
        except ValueError as exc:
            return error_response(str(exc), status.HTTP_400_BAD_REQUEST)
        return success_response(CarSerializer(updated_car).data, message="Car updated successfully")


class CarImagesView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def _check_staff_or_admin(self, request):
        role = getattr(request.user, "role", None)
        if role not in {"staff", "admin"}:
            return error_response("Only staff or admin can manage car images", status.HTTP_403_FORBIDDEN)
        return None

    def post(self, request, car_id):
        err = self._check_staff_or_admin(request)
        if err:
            return err

        car = CarService.get_car_by_id(car_id)
        if not car:
            return error_response("Car not found", status.HTTP_404_NOT_FOUND)

        image_files = request.FILES.getlist("images")
        try:
            updated_car = CarService.add_images(car, image_files)
        except ValueError as exc:
            return error_response(str(exc), status.HTTP_400_BAD_REQUEST)
        except UploadValidationError as exc:
            return error_response(str(exc), status.HTTP_400_BAD_REQUEST)
        except UploadFailedError as exc:
            return error_response(str(exc), status.HTTP_502_BAD_GATEWAY)

        return success_response(CarSerializer(updated_car).data, message="Images added successfully")

    def delete(self, request, car_id):
        err = self._check_staff_or_admin(request)
        if err:
            return err

        car = CarService.get_car_by_id(car_id)
        if not car:
            return error_response("Car not found", status.HTTP_404_NOT_FOUND)

        delete_all = str(request.data.get("delete_all", "")).lower() in {"true", "1", "yes"}
        if delete_all:
            updated_car = CarService.delete_all_images(car)
            return success_response(CarSerializer(updated_car).data, message="All images deleted successfully")

        image_url = (request.data.get("image_url") or "").strip()
        if not image_url:
            return error_response("Provide image_url to delete a specific image, or delete_all=true to remove all", status.HTTP_400_BAD_REQUEST)

        try:
            updated_car = CarService.delete_image(car, image_url)
        except ValueError as exc:
            return error_response(str(exc), status.HTTP_400_BAD_REQUEST)

        return success_response(CarSerializer(updated_car).data, message="Image deleted successfully")
