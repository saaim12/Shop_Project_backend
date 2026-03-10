from rest_framework import serializers


class InventorySerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    spare_part_id = serializers.CharField(read_only=True)
    spare_part_name = serializers.CharField(read_only=True)
    quantity = serializers.IntegerField(min_value=0, read_only=True)
    updated_by = serializers.CharField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def to_representation(self, instance):
        return {
            "id": str(instance.id),
            "spare_part_id": str(instance.spare_part.id),
            "spare_part_name": instance.spare_part.name,
            "quantity": instance.quantity,
            "updated_by": str(instance.updated_by.id) if instance.updated_by else None,
            "updated_at": instance.updated_at,
        }


class InventoryUpdateSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=0)
