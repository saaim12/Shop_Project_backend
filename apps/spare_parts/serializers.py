from bson import ObjectId
from rest_framework import serializers

from apps.cars.models import Car
from apps.spare_parts.models import SparePart


class SparePartSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=120)
    description = serializers.CharField(required=False, allow_blank=True)
    price = serializers.FloatField(min_value=0)
    quantity = serializers.FloatField(min_value=1, required=False, default=1)
    condition = serializers.ChoiceField(choices=["new", "used", "external"])
    images = serializers.ListField(child=serializers.CharField(), required=False, read_only=True)
    car_id = serializers.CharField(required=False, allow_blank=True)
    created_by = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    def validate_car_id(self, value):
        value = (value or "").strip()
        if not value:
            return None

        try:
            car = Car.objects(id=ObjectId(value)).first()
            if not car:
                raise serializers.ValidationError("Invalid car reference")
            return value
        except Exception as exc:
            raise serializers.ValidationError("Invalid car reference") from exc

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be positive")
        return value

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        return value

    def to_representation(self, instance):
        raw = instance.to_mongo().to_dict()

        car_ref = raw.get("car") or raw.get("car_reference")
        car_id = getattr(car_ref, "id", car_ref) if car_ref is not None else None

        created_by_ref = raw.get("created_by") or raw.get("added_by")
        created_by_id = getattr(created_by_ref, "id", created_by_ref) if created_by_ref is not None else None

        images = instance.images or []

        return {
            "id": str(instance.id),
            "name": instance.name,
            "description": instance.description,
            "price": instance.price,
            "quantity": instance.quantity,
            "condition": instance.condition,
            "images": images,
            "car_id": str(car_id) if car_id else None,
            "created_by": str(created_by_id) if created_by_id else None,
            "created_at": instance.created_at,
        }
