from django.db import models

from apps.core.models import BaseModel


class Permission(BaseModel):
    """
    Represents a permission that can be granted to roles.
    """
    code = models.CharField(max_length=100, unique=True)
    module = models.CharField(max_length=50)
    description = models.TextField()

    class Meta:
        db_table = 'permissions'
        ordering = ['module', 'code']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['module']),
        ]

    def __str__(self):
        return self.code
