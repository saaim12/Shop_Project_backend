from bson import ObjectId
from django.conf import settings

from apps.services.s3_service import S3Service
from apps.spare_parts.models import SparePart, SparePartImage


class SparePartService:
    @staticmethod
    def list_spare_parts(filters=None):
        query = SparePart.objects()
        filters = filters or {}
        for key, value in filters.items():
            if value in (None, ""):
                continue
            query = query.filter(**{key: value})
        return query.order_by("-created_at")

    @staticmethod
    def get_spare_part_by_id(part_id):
        try:
            return SparePart.objects(id=ObjectId(part_id)).first()
        except Exception:
            return None

    @staticmethod
    def create_spare_part(payload):
        part = SparePart(
            name=payload["name"],
            brand=payload["brand"],
            model=payload["model"],
            model_year=payload["model_year"],
            vehicle_type=payload["vehicle_type"],
            category=payload["category"],
            condition=payload["condition"],
            description=payload.get("description", ""),
            item_number=payload.get("item_number", ""),
            article_number=payload.get("article_number", ""),
            ditto_number=payload.get("ditto_number", ""),
            engine_code=payload.get("engine_code", ""),
            engine_spec=payload.get("engine_spec", ""),
            chassis_number=payload.get("chassis_number", ""),
            mileage=payload.get("mileage", 0),
            family_card_number=payload.get("family_card_number", ""),
            oem_numbers=payload.get("oem_numbers", ""),
            identification_numbers=payload.get("identification_numbers", ""),
        )
        part.save()
        return part

    @staticmethod
    def update_spare_part(part, payload):
        for field in [
            "name",
            "brand",
            "model",
            "model_year",
            "vehicle_type",
            "category",
            "condition",
            "description",
            "item_number",
            "article_number",
            "ditto_number",
            "engine_code",
            "engine_spec",
            "chassis_number",
            "mileage",
            "family_card_number",
            "oem_numbers",
            "identification_numbers",
        ]:
            if field in payload:
                setattr(part, field, payload[field])
        part.save()
        return part

    @staticmethod
    def delete_spare_part(part):
        for image in SparePartImage.objects(spare_part=part):
            try:
                S3Service().delete_image(image.image)
            except Exception:
                pass
            image.delete()
        part.delete()

    @staticmethod
    def add_images(part, image_files):
        if not image_files:
            raise ValueError("No images provided")
        created = []
        s3 = S3Service()
        for image_file in image_files:
            image_url = s3.upload_image(image_file, folder=settings.S3_SPARE_PARTS_FOLDER)
            image_doc = SparePartImage(spare_part=part, image=image_url)
            image_doc.save()
            created.append(image_doc)
        return created

    @staticmethod
    def delete_image(image_id):
        try:
            image = SparePartImage.objects(id=ObjectId(image_id)).first()
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
    def delete_all_images(part):
        for image in SparePartImage.objects(spare_part=part):
            try:
                S3Service().delete_image(image.image)
            except Exception:
                pass
            image.delete()

    @staticmethod
    def update_image(image_id, image_file):
        try:
            image_doc = SparePartImage.objects(id=ObjectId(image_id)).first()
        except Exception:
            image_doc = None
        if not image_doc:
            raise ValueError("Image not found")

        s3 = S3Service()
        try:
            s3.delete_image(image_doc.image)
        except Exception:
            pass

        image_doc.image = s3.upload_image(image_file, folder=settings.S3_SPARE_PARTS_FOLDER)
        image_doc.save()
        return image_doc
