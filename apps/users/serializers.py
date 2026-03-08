from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'user_type', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
