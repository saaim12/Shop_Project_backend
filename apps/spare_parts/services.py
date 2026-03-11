from bson import ObjectId
from django.conf import settings

from apps.cars.models import Car
from apps.services.s3_service import S3Service
from apps.spare_parts.models import SparePart


class SparePartService:
    @staticmethod
    def _resolve_car(car_id):
        if not car_id:
            return None

        try:
            car = Car.objects(id=ObjectId(car_id)).first()
        except Exception:
            car = None

        if not car:
            raise ValueError("Invalid car reference")

        return car

    @staticmethod
    def _validate_condition_with_car(condition, car):
        if condition == SparePart.CONDITION_USED and not car:
            raise ValueError("Used spare parts must reference a car")

        if condition in [SparePart.CONDITION_NEW, SparePart.CONDITION_EXTERNAL] and car:
            raise ValueError("New or external parts cannot reference a car")

    @staticmethod
    def _check_duplicate(name, description, exclude_id=None):
        name_normalized = (name or "").strip().lower()
        description_normalized = (description or "").strip().lower()

        # Check name uniqueness alone
        name_query = SparePart.objects(__raw__={"name": {"$regex": f"^{name_normalized}$", "$options": "i"}})
        if exclude_id:
            name_query = name_query.filter(id__ne=exclude_id)
        if name_query.first():
            raise ValueError("A spare part with this name already exists")

        # Check name + description combination
        combo_query = SparePart.objects(
            __raw__={
                "name": {"$regex": f"^{name_normalized}$", "$options": "i"},
                "description": {"$regex": f"^{description_normalized}$", "$options": "i"},
            }
        )
        if exclude_id:
            combo_query = combo_query.filter(id__ne=exclude_id)
        if combo_query.first():
            raise ValueError("A spare part with the same name and description already exists")

    @staticmethod
    def create_spare_part(payload, user, image_files=None):
        SparePartService._check_duplicate(payload["name"], payload.get("description", ""))

        car = SparePartService._resolve_car(payload.get("car_id"))
        condition = payload["condition"]
        SparePartService._validate_condition_with_car(condition, car)

        image_urls = []
        if image_files:
            s3_service = S3Service()
            for image_file in image_files:
                image_urls.append(s3_service.upload_image(image_file, folder=settings.S3_SPARE_PARTS_FOLDER))

        part = SparePart(
            name=payload["name"],
            description=payload.get("description", ""),
            category=payload.get("category", SparePart.CATEGORY_OTHER),
            price=payload["price"],
            quantity=payload.get("quantity", 1),
            condition=condition,
            images=image_urls,
            car=car,
            created_by=user,
        )
        part.save()
        return part

    @staticmethod
    def list_spare_parts(condition=None):
        query = SparePart.objects()
        if condition:
            query = query.filter(condition=condition)
        return query.order_by("-created_at")

    @staticmethod
    def get_spare_part_by_id(part_id):
        try:
            return SparePart.objects(id=ObjectId(part_id)).first()
        except Exception:
            return None

    @staticmethod
    def delete_spare_part(part):
        s3_service = S3Service()

        for url in list(part.images or []):
            try:
                s3_service.delete_image(url)
            except Exception:
                pass

        legacy_image = getattr(part, "image", "") or ""
        if legacy_image:
            try:
                s3_service.delete_image(legacy_image)
            except Exception:
                pass

        part.delete()

    @staticmethod
    def update_spare_part(part, payload):
        new_name = payload.get("name", part.name)
        new_description = payload.get("description", part.description)
        SparePartService._check_duplicate(new_name, new_description, exclude_id=part.id)

        car = None
        if payload.get("car_id"):
            car = SparePartService._resolve_car(payload["car_id"])

        condition = payload.get("condition", part.condition)
        SparePartService._validate_condition_with_car(condition, car)

        if "name" in payload:
            part.name = payload["name"]
        if "description" in payload:
            part.description = payload.get("description") or ""
        if "category" in payload:
            part.category = payload["category"]
        if "price" in payload:
            part.price = payload["price"]
        if "quantity" in payload:
            part.quantity = payload["quantity"]
        if "condition" in payload:
            part.condition = payload["condition"]

        if "car_id" in payload:
            part.car = car

        part.save()
        return part

    @staticmethod
    def add_images(part, image_files):
        if not image_files:
            raise ValueError("No images provided")
        s3_service = S3Service()
        for image_file in image_files:
            url = s3_service.upload_image(image_file, folder=settings.S3_SPARE_PARTS_FOLDER)
            part.images.append(url)
        part.save()
        return part

    @staticmethod
    def delete_image(part, image_url):
        if image_url not in part.images:
            raise ValueError("Image not found on this spare part")
        try:
            S3Service().delete_image(image_url)
        except Exception:
            pass
        part.images.remove(image_url)
        part.save()
        return part

    @staticmethod
    def delete_all_images(part):
        s3_service = S3Service()
        for url in list(part.images):
            try:
                s3_service.delete_image(url)
            except Exception:
                pass
        part.images = []
        part.save()
        return part

