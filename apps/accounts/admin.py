"""
Admin configuration for accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import (
    User, Role, Permission, UserRole,
    RolePermission, Invitation
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin for User model.
    """
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'created_at')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """
    Admin for Role model.
    """
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """
    Admin for Permission model.
    """
    list_display = ('code', 'module', 'description')
    list_filter = ('module',)
    search_fields = ('code', 'module', 'description')
    ordering = ('module', 'code')


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """
    Admin for UserRole model.
    """
    list_display = ('user', 'role', 'created_at')
    list_filter = ('role',)
    search_fields = ('user__email', 'role__name')
    ordering = ('-created_at',)


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    """
    Admin for RolePermission model.
    """
    list_display = ('role', 'permission', 'created_at')
    list_filter = ('role', 'permission')
    search_fields = ('role__name', 'permission__name')
    ordering = ('-created_at',)


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    """
    Admin for Invitation model.
    """
    list_display = ('email', 'status', 'invited_by', 'expires_at', 'created_at')
    list_filter = ('status',)
    search_fields = ('email', 'invited_by__email')
    ordering = ('-created_at',)
