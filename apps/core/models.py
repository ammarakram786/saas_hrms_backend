"""
Core models with soft delete functionality and multi-tenant support.
"""
import uuid
from django.db import models
from django.utils import timezone


class SoftDeleteManager(models.Manager):
    """Manager to exclude soft-deleted objects by default."""
    
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class AllObjectsManager(models.Manager):
    """Manager to include soft-deleted objects."""
    
    def get_queryset(self):
        return super().get_queryset()


class BaseModel(models.Model):
    """
    Abstract base model with soft delete functionality.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    # Managers
    objects = SoftDeleteManager()
    all_objects = AllObjectsManager()
    
    class Meta:
        abstract = True
    
    def delete(self, using=None, keep_parents=False):
        """Soft delete the object."""
        self.deleted_at = timezone.now()
        self.save(using=using)
    
    def hard_delete(self, using=None, keep_parents=False):
        """Permanently delete the object."""
        super().delete(using=using, keep_parents=keep_parents)
    
    def restore(self):
        """Restore a soft-deleted object."""
        self.deleted_at = None
        self.save()
    
    @property
    def is_deleted(self):
        """Check if object is soft-deleted."""
        return self.deleted_at is not None


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


class TimestampedModel(models.Model):
    """
    Abstract model with just timestamps (no soft delete).
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
