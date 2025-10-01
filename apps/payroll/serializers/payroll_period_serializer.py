"""
PayrollPeriod serializers.
"""
from rest_framework import serializers
from ..models import PayrollPeriod


class PayrollPeriodSerializer(serializers.ModelSerializer):
    """
    Serializer for PayrollPeriod model.
    """
    processed_by_name = serializers.CharField(source='processed_by.username', read_only=True)
    
    class Meta:
        model = PayrollPeriod
        fields = [
            'id', 'name', 'period_start', 'period_end', 'pay_date',
            'status', 'processed_by', 'processed_by_name', 'processed_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'processed_by_name', 'processed_at', 'created_at', 'updated_at']
