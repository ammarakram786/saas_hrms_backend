"""
Holiday serializers.
"""
from rest_framework import serializers
from ..models import Holiday


class HolidaySerializer(serializers.ModelSerializer):
    """
    Serializer for Holiday model.
    """
    
    class Meta:
        model = Holiday
        fields = [
            'id', 'name', 'date', 'is_optional', 'description',
            'created_at', 'updated_at'
        ]
