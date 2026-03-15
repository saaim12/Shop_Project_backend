from bson import ObjectId
from django.conf import settings

from apps.services.s3_service import S3Service
from apps.tyres.models import Tyre, TyreImage


class TyreService:
    @staticmethod
    def list_tyres(filters=None):
        query = Tyre.objects()
        filters = filters or {}
        for key, value in filters.items():
            if value in (None, ""):
                continue
            query = query.filter(**{key: value})
        return query.order_by("-created_at")

    @staticmethod
    def get_tyre_by_id(tyre_id):
        try:
            return Tyre.objects(id=ObjectId(tyre_id)).first()
        except Exception:
            return None

    @staticmethod
    def create_tyre(payload):
        tyre = Tyre(
            company=payload["company"],
            condition=payload["condition"],
            inches=payload["inches"],
            type=payload["type"],
            description=payload.get("description", ""),
        )
        tyre.save()
        return tyre

    @staticmethod
    def update_tyre(tyre, payload):
        for field in ["company", "condition", "inches", "type", "description"]:
            if field in payload:
                setattr(tyre, field, payload[field])
        tyre.save()
        return tyre

    @staticmethod
    def delete_tyre(tyre):
        for image in TyreImage.objects(tyre=tyre):
            try:
                S3Service().delete_image(image.image)
            except Exception:
                pass
            image.delete()
        tyre.delete()

    @staticmethod
    def add_images(tyre, image_files):
        if not image_files:
            raise ValueError("No images provided")
        s3 = S3Service()
        for image_file in image_files:
            image_url = s3.upload_image(image_file, folder=settings.S3_TYRES_FOLDER)
            TyreImage(tyre=tyre, image=image_url).save()

    @staticmethod
    def delete_image(image_id):
        try:
            image = TyreImage.objects(id=ObjectId(image_id)).first()
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
    def delete_all_images(tyre):
        for image in TyreImage.objects(tyre=tyre):
            try:
                S3Service().delete_image(image.image)
            except Exception:
                pass
            image.delete()

    @staticmethod
    def update_image(image_id, image_file):
        try:
            image_doc = TyreImage.objects(id=ObjectId(image_id)).first()
        except Exception:
            image_doc = None
        if not image_doc:
            raise ValueError("Image not found")

        s3 = S3Service()
        try:
            s3.delete_image(image_doc.image)
        except Exception:
            pass

        image_doc.image = s3.upload_image(image_file, folder=settings.S3_TYRES_FOLDER)
        image_doc.save()
        return image_doc
