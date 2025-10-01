"""
LeaveType serializers.
"""
from rest_framework import serializers
from ..models import LeaveType


class LeaveTypeSerializer(serializers.ModelSerializer):
    """
    Serializer for LeaveType model.
    """
    
    class Meta:
        model = LeaveType
        fields = [
            'id', 'name', 'code', 'description', 'days_allowed_per_year',
            'is_paid', 'requires_approval', 'can_be_carried_forward',
            'max_consecutive_days', 'applicable_gender', 'is_active',
            'created_at', 'updated_at'
        ]
