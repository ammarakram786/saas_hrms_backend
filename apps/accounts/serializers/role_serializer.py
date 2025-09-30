from rest_framework import serializers

from .permission_serializer import PermissionSerializer
from apps.accounts.models import Role


class RoleSerializer(serializers.ModelSerializer):
    """
    Serializer for Role model.
    """
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_codes = serializers.ReadOnlyField()
    user_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = [
            'id', 'name', 'description', 'is_system', 'is_active',
            'permissions', 'permission_codes', 'user_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_system']

    def get_user_count(self, obj):
        """Get number of users with this role."""
        return obj.user_roles.count()
