from bson import ObjectId

from apps.inventory.models import Inventory


class InventoryService:
    @staticmethod
    def list_inventory():
        return Inventory.objects().order_by("-updated_at")

    @staticmethod
    def get_inventory_item(inventory_id):
        try:
            return Inventory.objects(id=ObjectId(inventory_id)).first()
        except Exception:
            return None

    @staticmethod
    def update_inventory(item, payload, user):
        item.quantity = payload["quantity"]
        item.updated_by = user
        item.save()
        return item

