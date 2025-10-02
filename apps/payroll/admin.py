"""
Admin configuration for payroll app.
"""
from django.contrib import admin

from .models import PayrollPeriod, PayrollRecord, PayrollComponent


@admin.register(PayrollPeriod)
class PayrollPeriodAdmin(admin.ModelAdmin):
    """
    Admin for PayrollPeriod model.
    """
    list_display = ('name', 'period_start', 'period_end', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('name',)
    ordering = ('-period_start',)
    date_hierarchy = 'period_start'


@admin.register(PayrollRecord)
class PayrollRecordAdmin(admin.ModelAdmin):
    """
    Admin for PayrollRecord model.
    """
    list_display = ('employee', 'payroll_period', 'gross_pay', 'net_pay', 'created_at')
    list_filter = ('payroll_period',)
    search_fields = ('employee__first_name', 'employee__last_name', 'employee__employee_id')
    ordering = ('-created_at',)


@admin.register(PayrollComponent)
class PayrollComponentAdmin(admin.ModelAdmin):
    """
    Admin for PayrollComponent model.
    """
    list_display = ('name', 'component_type', 'calculation_method', 'created_at')
    list_filter = ('component_type', 'calculation_method')
    search_fields = ('name', 'description')
    ordering = ('name',)
