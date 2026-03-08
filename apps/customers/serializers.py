"""Customers serializers."""

from rest_framework import serializers

from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Customer
        fields = [
            "id",
            "user",
            "full_name",
            "first_name",
            "last_name",
            "email",
            "phone",
            "address",
            "city",
            "state",
            "zip_code",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "full_name", "created_at", "updated_at"]
