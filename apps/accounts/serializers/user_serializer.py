from rest_framework import serializers

from apps.accounts.models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    """
    full_name = serializers.ReadOnlyField()
    effective_permissions = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'is_active', 'last_login', 'profile', 'effective_permissions',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'last_login', 'created_at', 'updated_at',
            'full_name', 'effective_permissions'
        ]

