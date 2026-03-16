from bson import ObjectId
from mongoengine.errors import DoesNotExist as MongoDoesNotExist

from apps.cars.models import Car
from apps.cars.services import CarService
from apps.inventory.models import Inventory
from apps.rims.models import Rim
from apps.rims.services import RimService
from apps.spare_parts.models import SparePart
from apps.spare_parts.services import SparePartService
from apps.tyres.models import Tyre
from apps.tyres.services import TyreService
from apps.users.models import User


class InventoryService:
    PRODUCT_MODELS = {
        Inventory.CATEGORY_SPARE_PART: SparePart,
        Inventory.CATEGORY_CARS: Car,
        Inventory.CATEGORY_RIMS: Rim,
        Inventory.CATEGORY_TYRE: Tyre,
    }
    PRODUCT_DELETE_SERVICES = {
        Inventory.CATEGORY_SPARE_PART: SparePartService.delete_spare_part,
        Inventory.CATEGORY_CARS: CarService.delete_car,
        Inventory.CATEGORY_RIMS: RimService.delete_rim,
        Inventory.CATEGORY_TYRE: TyreService.delete_tyre,
    }

    @staticmethod
    def _ensure_staff_or_admin(user):
        role = (getattr(user, "role", "") or "").upper()
        if role not in {"STAFF", "ADMIN"}:
            raise ValueError("Only staff or admin can manage inventory")

    @staticmethod
    def _normalize_category(category):
        return (category or "").strip().lower()

    @staticmethod
    def _get_product(category, product_id):
        normalized_category = InventoryService._normalize_category(category)
        model = InventoryService.PRODUCT_MODELS.get(normalized_category)
        if not model:
            raise ValueError("Invalid category")

        try:
            obj_id = ObjectId(product_id)
        except Exception as exc:
            raise ValueError("Invalid product_id") from exc

        product = model.objects(id=obj_id).first()
        if not product:
            raise ValueError("Referenced product not found")
        return product

    @staticmethod
    def _get_user_filter(stored_by_id):
        try:
            return ObjectId(stored_by_id)
        except Exception as exc:
            raise ValueError("Invalid stored_by filter") from exc

    @staticmethod
    def _get_existing_stored_by_user(user):
        user_id = getattr(user, "id", None)
        if not user_id:
            raise ValueError("stored_by user not found")

        existing_user = User.objects(id=user_id).first()
        if not existing_user:
            raise ValueError("stored_by user not found")
        return existing_user

    @staticmethod
    def _delete_product(item):
        delete_service = InventoryService.PRODUCT_DELETE_SERVICES.get(item.category)
        if not delete_service:
            raise ValueError("Unsupported inventory category")

        try:
            product = item.product
        except MongoDoesNotExist as exc:
            raise ValueError("Referenced product not found for this inventory item") from exc

        if not product:
            raise ValueError("Referenced product not found for this inventory item")

        delete_service(product)

    @staticmethod
    def _cleanup_orphan_inventory_rows(queryset):
        orphan_ids = []
        for item in queryset:
            try:
                _ = item.product
            except MongoDoesNotExist:
                orphan_ids.append(item.id)

        if orphan_ids:
            Inventory.objects(id__in=orphan_ids).delete()

    @staticmethod
    def _build_filtered_queryset(category=None, stored_by_id=None):
        queryset = Inventory.objects()

        if category:
            normalized_category = InventoryService._normalize_category(category)
            if normalized_category not in Inventory.CATEGORY_CHOICES:
                raise ValueError("Invalid category filter")
            queryset = queryset.filter(category=normalized_category)

        if stored_by_id:
            queryset = queryset.filter(stored_by=InventoryService._get_user_filter(stored_by_id))

        return queryset

    @staticmethod
    def list_inventory(category=None, stored_by_id=None):
        queryset = InventoryService._build_filtered_queryset(category=category, stored_by_id=stored_by_id)
        InventoryService._cleanup_orphan_inventory_rows(queryset)
        queryset = InventoryService._build_filtered_queryset(category=category, stored_by_id=stored_by_id)
        return queryset.order_by("-created_at")

    @staticmethod
    def get_inventory_item(inventory_id):
        try:
            return Inventory.objects(id=ObjectId(inventory_id)).first()
        except Exception:
            return None

    @staticmethod
    def create_inventory(payload, user):
        InventoryService._ensure_staff_or_admin(user)
        stored_by_user = InventoryService._get_existing_stored_by_user(user)
        category = InventoryService._normalize_category(payload["category"])
        product = InventoryService._get_product(category, payload["product_id"])
        quantity = payload["quantity"]

        existing = Inventory.objects(category=category, product=product).first()
        if existing:
            existing.quantity += quantity
            if "storage_position" in payload:
                existing.storage_position = payload.get("storage_position", "")
            existing.stored_by = stored_by_user
            if existing.quantity == 0:
                InventoryService._delete_product(existing)
                existing.delete()
                return None
            existing.save()
            return existing

        if quantity == 0:
            return None

        item = Inventory(
            category=category,
            product=product,
            quantity=quantity,
            storage_position=payload.get("storage_position", ""),
            stored_by=stored_by_user,
        )
        item.save()
        return item

    @staticmethod
    def update_inventory(item, payload, user):
        InventoryService._ensure_staff_or_admin(user)
        stored_by_user = InventoryService._get_existing_stored_by_user(user)
        target_category = InventoryService._normalize_category(payload.get("category", item.category))

        if "category" in payload and "product_id" not in payload and target_category != item.category:
            raise ValueError("product_id is required when category changes")

        if "product_id" in payload or target_category != item.category:
            product_id = payload.get("product_id", str(item.product.id))
            item.product = InventoryService._get_product(target_category, product_id)
            item.category = target_category

        if "quantity" in payload:
            item.quantity = payload["quantity"]
        if "storage_position" in payload:
            item.storage_position = payload.get("storage_position", "")

        item.stored_by = stored_by_user
        if item.quantity == 0:
            InventoryService._delete_product(item)
            item.delete()
            return None

        item.save()
        return item

    @staticmethod
    def delete_inventory(item):
        InventoryService._delete_product(item)
        item.delete()
