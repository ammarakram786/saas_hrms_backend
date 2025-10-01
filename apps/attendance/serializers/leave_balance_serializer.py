"""
LeaveBalance serializers.
"""
from rest_framework import serializers
from ..models import LeaveBalance


class LeaveBalanceSerializer(serializers.ModelSerializer):
    """
    Serializer for LeaveBalance model.
    """
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    available_days = serializers.ReadOnlyField()
    total_allocated = serializers.ReadOnlyField()
    
    class Meta:
        model = LeaveBalance
        fields = [
            'id', 'employee', 'employee_name', 'leave_type', 'leave_type_name',
            'year', 'allocated_days', 'used_days', 'pending_days',
            'carried_forward', 'available_days', 'total_allocated',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'available_days', 'total_allocated', 'created_at', 'updated_at']
