from datetime import datetime

from rest_framework import serializers

from apps.cars.models import Car, CarImage


class CarImageSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    image = serializers.CharField()

    def to_representation(self, instance):
        return {
            "id": str(instance.id),
            "image": instance.image,
        }


class CarSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=150)
    brand = serializers.CharField(max_length=120)
    model = serializers.CharField(max_length=120)
    model_year = serializers.IntegerField(min_value=1951)
    year = serializers.IntegerField(min_value=1900)
    condition = serializers.ChoiceField(choices=Car.CONDITION_CHOICES)
    chassis_number = serializers.CharField(max_length=120)
    description = serializers.CharField(required=False, allow_blank=True)
    images = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def validate_condition(self, value):
        return (value or "").upper()

    def validate_model_year(self, value):
        current_year = datetime.utcnow().year
        if value <= 1950 or value > current_year:
            raise serializers.ValidationError("model_year must be greater than 1950 and less than or equal to current year")
        return value

    def get_images(self, instance):
        images = CarImage.objects(car=instance).order_by("-created_at")
        return CarImageSerializer(images, many=True).data

    def to_representation(self, instance):
        return {
            "id": str(instance.id),
            "name": instance.name,
            "brand": instance.brand,
            "model": instance.model,
            "model_year": instance.model_year,
            "year": instance.year,
            "condition": instance.condition,
            "chassis_number": instance.chassis_number,
            "description": instance.description,
            "images": self.get_images(instance),
            "created_at": instance.created_at,
            "updated_at": instance.updated_at,
        }
