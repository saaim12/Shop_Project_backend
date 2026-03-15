from bson import ObjectId
from django.conf import settings

from apps.rims.models import Rim, RimImage
from apps.services.s3_service import S3Service


class RimService:
    @staticmethod
    def list_rims(filters=None):
        query = Rim.objects()
        filters = filters or {}
        for key, value in filters.items():
            if value in (None, ""):
                continue
            query = query.filter(**{key: value})
        return query.order_by("-created_at")

    @staticmethod
    def get_rim_by_id(rim_id):
        try:
            return Rim.objects(id=ObjectId(rim_id)).first()
        except Exception:
            return None

    @staticmethod
    def create_rim(payload):
        rim = Rim(
            company=payload["company"],
            condition=payload["condition"],
            inches=payload["inches"],
            type=payload["type"],
            description=payload.get("description", ""),
        )
        rim.save()
        return rim

    @staticmethod
    def update_rim(rim, payload):
        for field in ["company", "condition", "inches", "type", "description"]:
            if field in payload:
                setattr(rim, field, payload[field])
        rim.save()
        return rim

    @staticmethod
    def delete_rim(rim):
        for image in RimImage.objects(rim=rim):
            try:
                S3Service().delete_image(image.image)
            except Exception:
                pass
            image.delete()
        rim.delete()

    @staticmethod
    def add_images(rim, image_files):
        if not image_files:
            raise ValueError("No images provided")
        s3 = S3Service()
        for image_file in image_files:
            image_url = s3.upload_image(image_file, folder=settings.S3_RIMS_FOLDER)
            RimImage(rim=rim, image=image_url).save()

    @staticmethod
    def delete_image(image_id):
        try:
            image = RimImage.objects(id=ObjectId(image_id)).first()
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
    def delete_all_images(rim):
        for image in RimImage.objects(rim=rim):
            try:
                S3Service().delete_image(image.image)
            except Exception:
                pass
            image.delete()

    @staticmethod
    def update_image(image_id, image_file):
        try:
            image_doc = RimImage.objects(id=ObjectId(image_id)).first()
        except Exception:
            image_doc = None
        if not image_doc:
            raise ValueError("Image not found")

        s3 = S3Service()
        try:
            s3.delete_image(image_doc.image)
        except Exception:
            pass

        image_doc.image = s3.upload_image(image_file, folder=settings.S3_RIMS_FOLDER)
        image_doc.save()
        return image_doc
