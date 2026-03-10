from bson import ObjectId
from rest_framework import serializers

from apps.cars.models import Car


class CarSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    number_plate = serializers.CharField(max_length=20)
    color = serializers.CharField(max_length=50)
    brand = serializers.CharField(max_length=100)
    model = serializers.CharField(max_length=100)
    year = serializers.IntegerField(min_value=1900)
    images = serializers.ListField(child=serializers.CharField(), required=False, read_only=True)
    created_by = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    def validate_number_plate(self, value):
        number_plate = (value or "").strip().upper()
        if not number_plate:
            raise serializers.ValidationError("Number plate is required")
        car_id = self.context.get("car_id")
        existing = Car.objects(number_plate=number_plate).first()
        if existing and (not car_id or str(existing.id) != car_id):
            raise serializers.ValidationError("Number plate already exists")
        return number_plate

    def validate_year(self, value):
        if not isinstance(value, int):
            raise serializers.ValidationError("Year must be numeric")
        return value

    def to_representation(self, instance):
        raw = instance.to_mongo().to_dict()
        created_by_ref = raw.get("created_by")
        created_by_id = None
        if created_by_ref is not None:
            created_by_id = getattr(created_by_ref, "id", created_by_ref)

        images = instance.images or []
        if not images and getattr(instance, "image", ""):
            images = [instance.image]

        return {
            "id": str(instance.id),
            "number_plate": instance.number_plate,
            "color": instance.color,
            "brand": instance.brand,
            "model": instance.model,
            "year": instance.year,
            "images": images,
            "created_by": str(created_by_id) if created_by_id else None,
            "created_at": instance.created_at,
        }


class CarIdSerializer(serializers.Serializer):
    car_id = serializers.CharField()

    def validate_car_id(self, value):
        try:
            ObjectId(value)
            return value
        except Exception as exc:
            raise serializers.ValidationError("Invalid car reference") from exc
