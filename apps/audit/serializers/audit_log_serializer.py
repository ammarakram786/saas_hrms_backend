"""
AuditLog serializers.
"""
from rest_framework import serializers
from ..models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    """
    Serializer for AuditLog model.
    """
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'actor_user_id', 'actor_username', 'actor_ip',
            'action', 'model_name', 'object_id', 'old_values',
            'new_values', 'changed_fields', 'description', 'metadata',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
