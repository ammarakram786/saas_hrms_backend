"""
Admin configuration for audit app.
"""
from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """
    Admin for AuditLog model.
    """
    list_display = ('actor_username', 'action', 'model_name', 'object_id', 'created_at')
    list_filter = ('action', 'model_name')
    search_fields = ('actor_username', 'model_name', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('actor_username', 'action', 'model_name', 'object_id', 'description', 'created_at')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
