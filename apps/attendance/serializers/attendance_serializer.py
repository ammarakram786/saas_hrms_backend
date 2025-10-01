"""
Attendance serializers.
"""
from rest_framework import serializers
from datetime import datetime
from ..models import AttendanceRecord


class AttendanceSerializer(serializers.ModelSerializer):
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
