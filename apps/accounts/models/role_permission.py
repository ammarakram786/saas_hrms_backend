from django.db import models

from apps.core.models import BaseModel
from .role import Role
from .permission import Permission


class RolePermission(BaseModel):
    """
    Many-to-many relationship between roles and permissions.
    """
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_permissions')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name='role_permissions')

    class Meta:
        db_table = 'role_permissions'
        unique_together = [('role', 'permission')]
