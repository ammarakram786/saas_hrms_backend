from django.db import models
from .base_model import BaseModel


class TenantAwareModel(BaseModel):
    """
    Abstract model that includes tenant_id for multi-tenant functionality.
    """
    tenant_id = models.UUIDField(db_index=True)

    class Meta:
        abstract = True

    @classmethod
    def get_tenant_queryset(cls, tenant_id):
        """Get queryset filtered by tenant."""
        return cls.objects.filter(tenant_id=tenant_id)