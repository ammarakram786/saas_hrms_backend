"""
Shift serializers.
"""
from rest_framework import serializers
from ..models import Shift


class ShiftSerializer(serializers.ModelSerializer):
    """
    Serializer for Shift model.
    """
    duration_hours = serializers.ReadOnlyField()
    
    class Meta:
        model = Shift
        fields = [
            'id', 'name', 'start_time', 'end_time', 'break_duration',
            'is_overnight', 'is_active', 'late_grace_period',
            'early_checkout_grace_period', 'duration_hours',
            'created_at', 'updated_at'
        ]
