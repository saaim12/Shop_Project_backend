from bson import ObjectId
from rest_framework import serializers

from apps.orders.models import Order
from apps.spare_parts.models import SparePart


class OrderCreateSerializer(serializers.Serializer):
    spare_part_id = serializers.CharField(required=False)
    quantity = serializers.IntegerField(required=False, min_value=1, default=1)
    spare_part_ids = serializers.ListField(child=serializers.CharField(), allow_empty=False, required=False)

    def validate_spare_part_id(self, value):
        try:
            if not SparePart.objects(id=ObjectId(value)).first():
                raise serializers.ValidationError(f"Spare part does not exist: {value}")
        except serializers.ValidationError:
            raise
        except Exception as exc:
            raise serializers.ValidationError(f"Invalid spare part id: {value}") from exc
        return value

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

    def validate(self, attrs):
        single_id = attrs.get("spare_part_id")
        many_ids = attrs.get("spare_part_ids")

        if not single_id and not many_ids:
            raise serializers.ValidationError("Provide spare_part_id")

        if single_id and many_ids:
            raise serializers.ValidationError("Provide either spare_part_id or spare_part_ids, not both")

        return attrs


class OrderSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    customer_id = serializers.CharField(read_only=True)
    spare_parts = serializers.ListField(read_only=True)
    total_price = serializers.FloatField(read_only=True)
    status = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    def to_representation(self, instance):
        primary_part = getattr(instance, "spare_part", None)
        if not primary_part and instance.spare_parts:
            primary_part = instance.spare_parts[0]

        return {
            "id": str(instance.id),
            "customer_id": str(instance.customer.id),
            "spare_part": {
                "id": str(primary_part.id),
                "name": primary_part.name,
                "price": primary_part.price,
            }
            if primary_part
            else None,
            "quantity": getattr(instance, "quantity", 1),
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
