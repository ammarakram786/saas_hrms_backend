from django.db import models


class SoftDeleteManager(models.Manager):
    """Manager to exclude soft-deleted objects by default."""

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class AllObjectsManager(models.Manager):
    """Manager to include soft-deleted objects."""

    def get_queryset(self):
        return super().get_queryset()

