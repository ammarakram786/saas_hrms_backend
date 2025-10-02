"""
Admin configuration for attendance app.
"""
from django.contrib import admin

from .models import (
    AttendanceRecord, LeaveType, LeaveBalance,
    LeaveRequest, Shift, Holiday
)


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    """
    Admin for AttendanceRecord model.
    """
    list_display = ('employee', 'date', 'check_in', 'check_out', 'status', 'hours_worked')
    list_filter = ('status', 'date')
    search_fields = ('employee__first_name', 'employee__last_name', 'employee__employee_id')
    ordering = ('-date', '-check_in')
    date_hierarchy = 'date'


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    """
    Admin for LeaveType model.
    """
    list_display = ('name', 'days_allowed_per_year', 'requires_approval', 'created_at')
    list_filter = ('requires_approval',)
    search_fields = ('name', 'description')
    ordering = ('name',)


@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    """
    Admin for LeaveBalance model.
    """
    list_display = ('employee', 'leave_type', 'year', 'allocated_days', 'used_days', 'available_days')
    list_filter = ('leave_type', 'year')
    search_fields = ('employee__first_name', 'employee__last_name', 'leave_type__name')
    ordering = ('-year', 'employee__last_name')


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    """
    Admin for LeaveRequest model.
    """
    list_display = ('employee', 'leave_type', 'start_date', 'end_date', 'status', 'approved_by')
    list_filter = ('status', 'leave_type')
    search_fields = ('employee__first_name', 'employee__last_name', 'reason')
    ordering = ('-start_date',)
    date_hierarchy = 'start_date'


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    """
    Admin for Shift model.
    """
    list_display = ('name', 'start_time', 'end_time', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('start_time',)


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    """
    Admin for Holiday model.
    """
    list_display = ('name', 'date', 'is_optional', 'created_at')
    list_filter = ('is_optional',)
    search_fields = ('name', 'description')
    ordering = ('date',)
    date_hierarchy = 'date'
