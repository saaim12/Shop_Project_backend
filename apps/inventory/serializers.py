from rest_framework import serializers
from bson import ObjectId

from apps.inventory.models import Inventory
from apps.spare_parts.models import SparePart


class InventorySerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    spare_part_id = serializers.CharField()
    quantity = serializers.IntegerField(min_value=0)
    storage_position = serializers.CharField(required=False, allow_blank=True)
    added_by = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def validate_spare_part_id(self, value):
        try:
            obj_id = ObjectId(value)
        except Exception as exc:
            raise serializers.ValidationError("Invalid spare_part_id") from exc

        if not SparePart.objects(id=obj_id).first():
            raise serializers.ValidationError("Referenced spare part not found")
        return value

    def to_representation(self, instance):
        return {
            "id": str(instance.id),
            "spare_part_id": str(instance.spare_part.id),
            "quantity": instance.quantity,
            "storage_position": instance.storage_position,
            "added_by": str(instance.added_by.id) if instance.added_by else None,
            "created_at": instance.created_at,
            "updated_at": instance.updated_at,
        }
