from bson import ObjectId
from rest_framework import serializers

from apps.users.models import User


class UserSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=120)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20)
    image = serializers.CharField(required=False, allow_blank=True)
    role = serializers.ChoiceField(choices=["customer", "staff", "admin"], default="customer")
    created_at = serializers.DateTimeField(read_only=True)

    def to_representation(self, instance):
        return {
            "id": str(instance.id),
            "name": instance.name,
            "email": instance.email,
            "phone": instance.phone,
            "image": instance.image or "",
            "role": instance.role,
            "created_at": instance.created_at,
        }


class RegisterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=120)
    email = serializers.CharField(max_length=255)
    password = serializers.CharField(min_length=8, write_only=True)
    phone = serializers.CharField(max_length=20)
    role = serializers.ChoiceField(choices=["customer", "staff", "admin"], default="customer")
    key = serializers.CharField(required=False, allow_blank=True)
    image = serializers.FileField(required=False, write_only=True)

    def validate_email(self, value):
        email = (value or "").strip().lower()
        if "@" not in email:
            raise serializers.ValidationError("Email address is not valid")
        if User.objects(email=email).first():
            raise serializers.ValidationError("User with this email already exists")
        return email

    def validate_password(self, value):
        if len(value or "") < 8:
            raise serializers.ValidationError("Password must contain at least 8 characters")
        return value

    def validate_phone(self, value):
        if not (value or "").strip():
            raise serializers.ValidationError("Phone must not be empty")
        return value


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        email = (value or "").strip().lower()
        if "@" not in email:
            raise serializers.ValidationError("Email address is not valid")
        return email


class UpdateProfileSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=120, required=False)
    phone = serializers.CharField(max_length=20, required=False)
    image = serializers.FileField(required=False, write_only=True)


class UserDeleteSerializer(serializers.Serializer):
    user_id = serializers.CharField()

    def validate_user_id(self, value):
        try:
            ObjectId(value)
            return value
        except Exception as exc:
            raise serializers.ValidationError("Invalid user id") from exc