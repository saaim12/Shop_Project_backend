from datetime import datetime

from rest_framework import serializers

from apps.spare_parts.models import SparePart, SparePartImage


class SparePartImageSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    image = serializers.CharField()

    def to_representation(self, instance):
        return {
            "id": str(instance.id),
            "image": instance.image,
        }


class SparePartSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=150)
    brand = serializers.CharField(max_length=120)
    model = serializers.CharField(max_length=120)
    model_year = serializers.IntegerField(min_value=1951)
    vehicle_type = serializers.ChoiceField(choices=SparePart.VEHICLE_TYPE_CHOICES)
    category = serializers.ChoiceField(choices=SparePart.CATEGORY_CHOICES)
    condition = serializers.ChoiceField(choices=SparePart.CONDITION_CHOICES)
    description = serializers.CharField(required=False, allow_blank=True)
    item_number = serializers.CharField(required=False, allow_blank=True)
    article_number = serializers.CharField(required=False, allow_blank=True)
    ditto_number = serializers.CharField(required=False, allow_blank=True)
    engine_code = serializers.CharField(required=False, allow_blank=True)
    engine_spec = serializers.CharField(required=False, allow_blank=True)
    chassis_number = serializers.CharField(required=False, allow_blank=True)
    mileage = serializers.IntegerField(required=False, min_value=0)
    family_card_number = serializers.CharField(required=False, allow_blank=True)
    oem_numbers = serializers.CharField(required=False, allow_blank=True)
    identification_numbers = serializers.CharField(required=False, allow_blank=True)
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
        images = SparePartImage.objects(spare_part=instance).order_by("-created_at")
        return SparePartImageSerializer(images, many=True).data

    def to_representation(self, instance):
        return {
            "id": str(instance.id),
            "name": instance.name,
            "brand": instance.brand,
            "model": instance.model,
            "model_year": instance.model_year,
            "vehicle_type": instance.vehicle_type,
            "category": instance.category,
            "condition": instance.condition,
            "description": instance.description,
            "item_number": instance.item_number,
            "article_number": instance.article_number,
            "ditto_number": instance.ditto_number,
            "engine_code": instance.engine_code,
            "engine_spec": instance.engine_spec,
            "chassis_number": instance.chassis_number,
            "mileage": instance.mileage,
            "family_card_number": instance.family_card_number,
            "oem_numbers": instance.oem_numbers,
            "identification_numbers": instance.identification_numbers,
            "images": self.get_images(instance),
            "created_at": instance.created_at,
            "updated_at": instance.updated_at,
        }


class SparePartImageWriteSerializer(serializers.Serializer):
    image = serializers.FileField(required=True)


class SparePartImageUpdateSerializer(serializers.Serializer):
    image = serializers.FileField(required=True)
