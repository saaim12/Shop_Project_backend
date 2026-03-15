from rest_framework import serializers

from apps.rims.models import Rim, RimImage


class RimImageSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    image = serializers.CharField()

    def to_representation(self, instance):
        return {
            "id": str(instance.id),
            "image": instance.image,
        }


class RimSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    company = serializers.CharField(max_length=120)
    condition = serializers.ChoiceField(choices=Rim.CONDITION_CHOICES)
    inches = serializers.FloatField(min_value=1)
    type = serializers.CharField(max_length=120)
    description = serializers.CharField(required=False, allow_blank=True)
    images = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def validate_condition(self, value):
        return (value or "").upper()

    def get_images(self, instance):
        images = RimImage.objects(rim=instance).order_by("-created_at")
        return RimImageSerializer(images, many=True).data

    def to_representation(self, instance):
        return {
            "id": str(instance.id),
            "company": instance.company,
            "condition": instance.condition,
            "inches": instance.inches,
            "type": instance.type,
            "description": instance.description,
            "images": self.get_images(instance),
            "created_at": instance.created_at,
            "updated_at": instance.updated_at,
        }
