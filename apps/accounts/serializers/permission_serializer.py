from rest_framework import serializers

from apps.accounts.models import Permission


class PermissionSerializer(serializers.ModelSerializer):
    """
    Serializer for Permission model.
    """
    class Meta:
        model = Permission
        fields = ['id', 'code', 'module', 'description']

