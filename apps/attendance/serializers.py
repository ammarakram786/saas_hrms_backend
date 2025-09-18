"""
Attendance serializers.
"""
from rest_framework import serializers
from django.db import transaction
from datetime import datetime, date

from .models import (
    AttendanceRecord, LeaveType, LeaveBalance, 
    LeaveRequest, Shift, Holiday
)


class AttendanceRecordSerializer(serializers.ModelSerializer):
    """
    Serializer for AttendanceRecord model.
    """
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    is_late = serializers.SerializerMethodField()
    
    class Meta:
        model = AttendanceRecord
        fields = [
            'id', 'employee', 'employee_name', 'employee_id', 'date',
            'check_in', 'check_out', 'break_start', 'break_end',
            'status', 'shift', 'hours_worked', 'overtime_hours',
            'leave_type', 'notes', 'is_manual_entry', 'is_late',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'hours_worked', 'overtime_hours', 'created_at', 'updated_at']
    
    def get_is_late(self, obj):
        """Check if employee was late."""
        return obj.is_late()


class ClockInSerializer(serializers.Serializer):
    """
    Serializer for clock-in action.
    """
    check_in_time = serializers.DateTimeField(default=datetime.now)
    shift = serializers.CharField(default='regular')
    notes = serializers.CharField(required=False, allow_blank=True)


class ClockOutSerializer(serializers.Serializer):
    """
    Serializer for clock-out action.
    """
    check_out_time = serializers.DateTimeField(default=datetime.now)
    notes = serializers.CharField(required=False, allow_blank=True)


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
            'id', 'approved_by', 'approved_by_name', 'approved_at',
            'created_at', 'updated_at'
        ]
    
    def validate(self, data):
        """
        Validate leave request data.
        """
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("Start date cannot be after end date.")
        
        if data['start_date'] < date.today():
            raise serializers.ValidationError("Cannot request leave for past dates.")
        
        return data
    
    def create(self, validated_data):
        """
        Create leave request with tenant context.
        """
        request = self.context.get('request')
        tenant_id = getattr(request, 'tenant_id', None)
        
        if tenant_id:
            validated_data['tenant_id'] = tenant_id
        
        leave_request = LeaveRequest.objects.create(**validated_data)
        
        # Update pending days in balance
        try:
            balance = LeaveBalance.objects.get(
                tenant_id=tenant_id,
                employee=leave_request.employee,
                leave_type=leave_request.leave_type,
                year=leave_request.start_date.year
            )
            balance.pending_days += leave_request.days_requested
            balance.save()
        except LeaveBalance.DoesNotExist:
            pass  # Handle this in view or create balance
        
        return leave_request


class LeaveRequestActionSerializer(serializers.Serializer):
    """
    Serializer for leave request approval/rejection actions.
    """
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    reason = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        """
        Validate action data.
        """
        if data['action'] == 'reject' and not data.get('reason'):
            raise serializers.ValidationError("Reason is required for rejection.")
        
        return data


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
