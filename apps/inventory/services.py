from bson import ObjectId

from apps.inventory.models import Inventory
from apps.services.s3_service import S3Service
from apps.spare_parts.models import SparePart
from apps.spare_parts.models import SparePartImage


class InventoryService:
    @staticmethod
    def _get_spare_part(spare_part_id):
        try:
            obj_id = ObjectId(spare_part_id)
        except Exception as exc:
            raise ValueError("Invalid spare_part_id") from exc

        spare_part = SparePart.objects(id=obj_id).first()
        if not spare_part:
            raise ValueError("Referenced spare part not found")
        return spare_part

    @staticmethod
    def _delete_spare_part_with_images(spare_part):
        for image_doc in SparePartImage.objects(spare_part=spare_part):
            try:
                S3Service().delete_image(image_doc.image)
            except Exception:
                pass
            image_doc.delete()
        spare_part.delete()

    @staticmethod
    def list_inventory():
        return Inventory.objects().order_by("-created_at")

    @staticmethod
    def get_inventory_item(inventory_id):
        try:
            return Inventory.objects(id=ObjectId(inventory_id)).first()
        except Exception:
            return None

    @staticmethod
    def create_inventory(payload, user):
        spare_part = InventoryService._get_spare_part(payload["spare_part_id"])
        quantity = payload["quantity"]

        existing = Inventory.objects(spare_part=spare_part).first()
        if existing:
            existing.quantity += quantity
            if "storage_position" in payload:
                existing.storage_position = payload.get("storage_position", "")
            existing.added_by = user
            if existing.quantity == 0:
                InventoryService._delete_spare_part_with_images(existing.spare_part)
                existing.delete()
                return None
            existing.save()
            return existing

        if quantity == 0:
            InventoryService._delete_spare_part_with_images(spare_part)
            return None

        item = Inventory(
            spare_part=spare_part,
            quantity=quantity,
            storage_position=payload.get("storage_position", ""),
            added_by=user,
        )
        item.save()
        return item

    @staticmethod
    def update_inventory(item, payload, user):
        if "quantity" in payload:
            item.quantity = payload["quantity"]
        if "storage_position" in payload:
            item.storage_position = payload.get("storage_position", "")
        if "spare_part_id" in payload:
            item.spare_part = InventoryService._get_spare_part(payload["spare_part_id"])

        item.added_by = user
        if item.quantity == 0:
            InventoryService._delete_spare_part_with_images(item.spare_part)
            item.delete()
            return None

        item.save()
        return item

    @staticmethod
    def delete_inventory(item):
        item.delete()
