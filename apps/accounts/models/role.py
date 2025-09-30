from django.db import models

from .permission import Permission
from apps.core.models import TenantAwareModel


class Role(TenantAwareModel):
    """
    Represents a role that can be assigned to users.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_system = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    permissions = models.ManyToManyField(Permission, through='RolePermission', through_fields=('role', 'permission'),
                                         blank=True)

    class Meta:
        db_table = 'roles'
        ordering = ['name']
        unique_together = [('tenant_id', 'name')]
        indexes = [
            models.Index(fields=['tenant_id', 'name']),
            models.Index(fields=['is_system']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.tenant_id})"

    @property
    def permission_codes(self):
        """Get list of permission codes for this role."""
        return list(self.permissions.values_list('code', flat=True))

    def add_permission(self, permission_code):
        """Add a permission to this role."""
        try:
            permission = Permission.objects.get(code=permission_code)
            RolePermission.objects.get_or_create(
                role=self,
                permission=permission
            )
        except Permission.DoesNotExist:
            raise ValueError(f"Permission '{permission_code}' does not exist")

    def remove_permission(self, permission_code):
        """Remove a permission from this role."""
        try:
            permission = Permission.objects.get(code=permission_code)
            RolePermission.objects.filter(
                role=self,
                permission=permission
            ).delete()
        except Permission.DoesNotExist:
            pass  # Permission doesn't exist, nothing to remove
