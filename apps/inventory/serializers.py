from rest_framework import serializers

from apps.inventory.models import Inventory


class InventorySerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    category = serializers.ChoiceField(choices=Inventory.CATEGORY_CHOICES, required=False)
    product_id = serializers.CharField(required=False)
    spare_part_id = serializers.CharField(required=False, write_only=True)
    quantity = serializers.IntegerField(min_value=0)
    storage_position = serializers.CharField(required=False, allow_blank=True)
    stored_by = serializers.CharField(read_only=True)
    product_name = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def validate(self, attrs):
        spare_part_id = attrs.pop("spare_part_id", None)
        if spare_part_id:
            attrs.setdefault("category", Inventory.CATEGORY_SPARE_PART)
            attrs["product_id"] = spare_part_id

        if not self.partial:
            if "category" not in attrs:
                raise serializers.ValidationError({"category": "This field is required."})
            if "product_id" not in attrs:
                raise serializers.ValidationError({"product_id": "This field is required."})

        if "category" in attrs:
            attrs["category"] = attrs["category"].strip().lower()

        return attrs

    @staticmethod
    def _get_product_name(product):
        for attr in ("name", "brand", "company", "model", "type"):
            value = getattr(product, attr, "")
            if value:
                return value
        return str(getattr(product, "id", ""))

    def to_representation(self, instance):
        product = instance.product
        return {
            "id": str(instance.id),
            "category": instance.category,
            "product_id": str(product.id),
            "product_name": self._get_product_name(product),
            "quantity": instance.quantity,
            "storage_position": instance.storage_position,
            "stored_by": str(instance.stored_by.id) if instance.stored_by else None,
            "created_at": instance.created_at,
            "updated_at": instance.updated_at,
        }
