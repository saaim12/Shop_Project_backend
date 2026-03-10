from bson import ObjectId
from rest_framework import serializers

from apps.orders.models import Order
from apps.spare_parts.models import SparePart


class OrderCreateSerializer(serializers.Serializer):
    spare_part_ids = serializers.ListField(child=serializers.CharField(), allow_empty=False)

    def validate_spare_part_ids(self, value):
        if not value:
            raise serializers.ValidationError("At least one spare part is required")

        for part_id in value:
            try:
                if not SparePart.objects(id=ObjectId(part_id)).first():
                    raise serializers.ValidationError(f"Spare part does not exist: {part_id}")
            except serializers.ValidationError:
                raise
            except Exception as exc:
                raise serializers.ValidationError(f"Invalid spare part id: {part_id}") from exc

        return value


class OrderSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    customer_id = serializers.CharField(read_only=True)
    spare_parts = serializers.ListField(read_only=True)
    total_price = serializers.FloatField(read_only=True)
    status = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    def to_representation(self, instance):
        return {
            "id": str(instance.id),
            "customer_id": str(instance.customer.id),
            "spare_parts": [
                {
                    "id": str(part.id),
                    "name": part.name,
                    "price": part.price,
                }
                for part in instance.spare_parts
            ],
            "total_price": instance.total_price,
            "status": instance.status,
            "created_at": instance.created_at,
        }


class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.STATUSES)
