"""
Admin configuration for employees app.
"""
from django.contrib import admin

from .models import Employee, Department, EmployeeDocument


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """
    Admin for Employee model.
    """
    list_display = ('employee_id', 'first_name', 'last_name', 'department', 'position', 'status')
    list_filter = ('status', 'department', 'employment_type')
    search_fields = ('employee_id', 'first_name', 'last_name', 'email', 'position')
    ordering = ('last_name', 'first_name')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('employee_id', 'first_name', 'last_name', 'email', 'phone')
        }),
        ('Employment Details', {
            'fields': ('department', 'position', 'employment_type', 'status', 'manager')
        }),
        ('Dates', {
            'fields': ('hire_date', 'end_date')
        }),
        ('Additional Information', {
            'fields': ('address', 'emergency_contact', 'notes'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """
    Admin for Department model.
    """
    list_display = ('name', 'code', 'parent', 'head', 'created_at')
    list_filter = ('parent',)
    search_fields = ('name', 'code', 'description')
    ordering = ('name',)


@admin.register(EmployeeDocument)
class EmployeeDocumentAdmin(admin.ModelAdmin):
    """
    Admin for EmployeeDocument model.
    """
    list_display = ('employee', 'document_type', 'uploaded_by', 'created_at')
    list_filter = ('document_type',)
    search_fields = ('employee__first_name', 'employee__last_name', 'document_type', 'notes')
    ordering = ('-created_at',)
