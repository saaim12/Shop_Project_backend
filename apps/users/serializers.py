from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):

    id = serializers.SerializerMethodField()
    image = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "password",
            "phone",
            "user_type",
            "age",
            "image",
            "is_active",
            "is_staff",
            "is_superuser",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "image",
            "is_staff",
            "is_superuser",
        ]

        extra_kwargs = {
            "password": {"write_only": True},
            "phone": {"required": True},
            "age": {"required": True},
        }

    def get_id(self, obj):
        return str(obj.id)

    def validate_email(self, value):
        """Ensure email uniqueness and normalized storage."""
        email = (value or "").strip().lower()
        if not email:
            raise serializers.ValidationError("Email is required.")

        normalized_email = User.objects.normalize_email(email)
        qs = User.objects.filter(email=normalized_email)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError("A user with this email already exists.")

        return normalized_email

    def validate_password(self, value):
        password = (value or "").strip()

        if not password:
            raise serializers.ValidationError("Password is required.")

        if len(password) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")

        if password.isdigit() or password.isalpha():
            raise serializers.ValidationError("Password must include both letters and numbers.")

        return password

    def validate_age(self, value):
        if value is None:
            raise serializers.ValidationError("Age is required.")

        if value < 18:
            raise serializers.ValidationError("Age must be 18 or older.")

        return value

    def validate_phone(self, value):
        phone = (value or "").strip()

        if not phone:
            raise serializers.ValidationError("Phone number is required.")

        return phone

    def validate(self, attrs):
        if not self.instance and not attrs.get("password"):
            raise serializers.ValidationError({"password": "Password is required."})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)