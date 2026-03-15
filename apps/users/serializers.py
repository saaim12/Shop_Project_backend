import re
from rest_framework import serializers
from apps.users.models import User


class UserSerializer(serializers.Serializer):

    id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=120)
    email = serializers.EmailField()
    age = serializers.IntegerField(min_value=18, max_value=90)
    phone_number = serializers.CharField(max_length=20)
    role = serializers.ChoiceField(choices=["CUSTOMER", "STAFF", "ADMIN"])
    image = serializers.CharField(required=False, allow_blank=True)

    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def to_representation(self, instance):

        return {
            "id": str(instance.id),
            "name": instance.name,
            "email": instance.email,
            "age": instance.age,
            "phone_number": instance.phone_number,
            "role": instance.role,
            "image": instance.image or "",
            "created_at": instance.created_at,
            "updated_at": instance.updated_at,
        }


class RegisterSerializer(serializers.Serializer):

    name = serializers.CharField(max_length=120)

    email = serializers.EmailField()

    age = serializers.IntegerField(min_value=18, max_value=90)

    password = serializers.CharField(min_length=8, write_only=True)

    phone_number = serializers.CharField(max_length=20)

    role = serializers.CharField(required=False, default="CUSTOMER")
    image = serializers.CharField(required=False, allow_blank=True)
    key = serializers.CharField(required=False, allow_blank=True, write_only=True)

    def validate_email(self, value):

        email = value.lower().strip()

        if User.objects(email=email).first():
            raise serializers.ValidationError("Email already exists")

        return email

    def validate_password(self, value):
        if len(value or "") < 8:
            raise serializers.ValidationError("Password must be at least 8 characters")

        if not re.search(r"[A-Za-z]", value):
            raise serializers.ValidationError(
                "Password must contain letters"
            )

        if not re.search(r"[0-9]", value):
            raise serializers.ValidationError(
                "Password must contain numbers"
            )

        return value

    def validate_role(self, value):
        role = (value or "CUSTOMER").strip().upper()
        if role not in {"CUSTOMER", "STAFF", "ADMIN"}:
            raise serializers.ValidationError("Invalid role")
        return role


class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField()

    password = serializers.CharField(write_only=True)


class UpdateProfileSerializer(serializers.Serializer):

    name = serializers.CharField(max_length=120, required=False)

    email = serializers.EmailField(required=False)

    age = serializers.IntegerField(min_value=18, max_value=90, required=False)

    phone_number = serializers.CharField(max_length=20, required=False)
    image = serializers.CharField(required=False, allow_blank=True)

    old_password = serializers.CharField(min_length=8, required=False, write_only=True)
    new_password = serializers.CharField(min_length=8, required=False, write_only=True)

    def validate_email(self, value):

        email = value.lower().strip()

        existing = User.objects(email=email).first()

        if existing and str(existing.id) != str(self.context.get("user_id", "")):
            raise serializers.ValidationError("Email already exists")

        return email

    def validate(self, attrs):
        old_password = attrs.get("old_password")
        new_password = attrs.get("new_password")
        if old_password and not new_password:
            raise serializers.ValidationError("new_password is required when old_password is provided")
        if new_password and not old_password:
            raise serializers.ValidationError("old_password is required when new_password is provided")

        if new_password:
            if not re.search(r"[A-Za-z]", new_password):
                raise serializers.ValidationError("Password must contain letters")
            if not re.search(r"[0-9]", new_password):
                raise serializers.ValidationError("Password must contain numbers")
        return attrs