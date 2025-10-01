"""
LeaveRequest serializers.
"""
from rest_framework import serializers
from django.db import transaction
from ..models import LeaveRequest, LeaveBalance


class LeaveRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for LeaveRequest model.
    """
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.full_name', read_only=True)
    
    class Meta:
        model = LeaveRequest
        fields = [
            'id', 'employee', 'employee_name', 'leave_type', 'leave_type_name',
            'start_date', 'end_date', 'days_requested', 'reason', 'status',
            'approved_by', 'approved_by_name', 'approved_at', 'rejection_reason',
            'documents', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'approved_by_name', 'approved_at', 'created_at', 'updated_at'
        ]
    
    def validate(self, attrs):
        """
        Validate leave request.
        """
        if attrs['start_date'] > attrs['end_date']:
            raise serializers.ValidationError(
                "Start date cannot be after end date."
            )
        
        # Check leave balance
        try:
            balance = LeaveBalance.objects.get(
                employee=attrs['employee'],
                leave_type=attrs['leave_type'],
                year=attrs['start_date'].year
            )
            
            if balance.available_days < attrs['days_requested']:
                raise serializers.ValidationError(
                    "Insufficient leave balance."
                )
        except LeaveBalance.DoesNotExist:
            raise serializers.ValidationError(
                "Leave balance not found for this employee and leave type."
            )
        
        return attrs
    
    @transaction.atomic
    def create(self, validated_data):
        """
        Create leave request and update pending days.
        """
        leave_request = LeaveRequest.objects.create(**validated_data)
        
        # Update pending days in leave balance
        balance = LeaveBalance.objects.get(
            employee=leave_request.employee,
            leave_type=leave_request.leave_type,
            year=leave_request.start_date.year
        )
        balance.pending_days += leave_request.days_requested
        balance.save()
        
        return leave_request


class LeaveApprovalSerializer(serializers.Serializer):
    """
    Serializer for leave approval/rejection.
    """
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    reason = serializers.CharField(required=False, allow_blank=True)
