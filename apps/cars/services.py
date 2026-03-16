from bson import ObjectId
from django.conf import settings
from mongoengine.errors import NotUniqueError

from apps.cars.models import Car, CarImage
from apps.services.s3_service import S3Service


class CarService:
    @staticmethod
    def _ensure_unique_fields(payload, current_car=None):
        chassis_number = payload.get("chassis_number")
        if chassis_number:
            existing = Car.objects(chassis_number=chassis_number).first()
            if existing and (not current_car or str(existing.id) != str(current_car.id)):
                raise ValueError("A car with this chassis number already exists")

        number_plate = payload.get("number_plate")
        if number_plate:
            existing = Car.objects(number_plate=number_plate).first()
            if existing and (not current_car or str(existing.id) != str(current_car.id)):
                raise ValueError("A car with this number plate already exists")

    @staticmethod
    def list_cars(filters=None):
        query = Car.objects()
        filters = filters or {}
        for key, value in filters.items():
            if value in (None, ""):
                continue
            query = query.filter(**{key: value})
        return query.order_by("-created_at")

    @staticmethod
    def get_car_by_id(car_id):
        try:
            return Car.objects(id=ObjectId(car_id)).first()
        except Exception:
            return None

    @staticmethod
    def create_car(payload):
        CarService._ensure_unique_fields(payload)
        car = Car(
            name=payload["name"],
            brand=payload["brand"],
            model=payload["model"],
            model_year=payload["model_year"],
            year=payload["year"],
            condition=payload["condition"],
            chassis_number=payload["chassis_number"],
            description=payload.get("description", ""),
        )
        try:
            car.save()
        except NotUniqueError as exc:
            error_text = str(exc)
            if "chassis_number" in error_text:
                raise ValueError("A car with this chassis number already exists") from exc
            if "number_plate" in error_text:
                raise ValueError("A car with this number plate already exists") from exc
            raise ValueError("Duplicate unique field value") from exc
        return car

    @staticmethod
    def update_car(car, payload):
        CarService._ensure_unique_fields(payload, current_car=car)
        for field in ["name", "brand", "model", "model_year", "year", "condition", "chassis_number", "description"]:
            if field in payload:
                setattr(car, field, payload[field])
        try:
            car.save()
        except NotUniqueError as exc:
            error_text = str(exc)
            if "chassis_number" in error_text:
                raise ValueError("A car with this chassis number already exists") from exc
            if "number_plate" in error_text:
                raise ValueError("A car with this number plate already exists") from exc
            raise ValueError("Duplicate unique field value") from exc
        return car

    @staticmethod
    def delete_car(car):
        for image in CarImage.objects(car=car):
            try:
                S3Service().delete_image(image.image)
            except Exception:
                pass
            image.delete()
        car.delete()

    @staticmethod
    def add_images(car, image_files):
        if not image_files:
            raise ValueError("No images provided")
        s3 = S3Service()
        for image_file in image_files:
            image_url = s3.upload_image(image_file, folder=settings.S3_CARS_FOLDER)
            CarImage(car=car, image=image_url).save()

    @staticmethod
    def delete_image(image_id):
        try:
            image = CarImage.objects(id=ObjectId(image_id)).first()
        except Exception:
            image = None
        if not image:
            raise ValueError("Image not found")
        try:
            S3Service().delete_image(image.image)
        except Exception:
            pass
        image.delete()

    @staticmethod
    def delete_all_images(car):
        for image in CarImage.objects(car=car):
            try:
                S3Service().delete_image(image.image)
            except Exception:
                pass
            image.delete()

    @staticmethod
    def update_image(image_id, image_file):
        try:
            image_doc = CarImage.objects(id=ObjectId(image_id)).first()
        except Exception:
            image_doc = None
        if not image_doc:
            raise ValueError("Image not found")

        s3 = S3Service()
        try:
            s3.delete_image(image_doc.image)
        except Exception:
            pass

        image_doc.image = s3.upload_image(image_file, folder=settings.S3_CARS_FOLDER)
        image_doc.save()
        return image_doc
