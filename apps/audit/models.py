"""
Audit logging models.
"""
from django.db import models
from django.db.models import JSONField
from apps.core.models import TenantAwareModel
from apps.core.utils import get_client_ip, get_user_agent


class AuditLog(TenantAwareModel):
    """
    Audit log for tracking user actions.
    """
    actor_user_id = models.UUIDField(null=True, blank=True)
    action = models.CharField(max_length=100)
    object_type = models.CharField(max_length=50)
    object_id = models.UUIDField(null=True, blank=True)
    diff = JSONField(default=dict, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'audit_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['tenant_id', 'actor_user_id']),
            models.Index(fields=['tenant_id', 'action']),
            models.Index(fields=['object_type', 'object_id']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.action} on {self.object_type} at {self.timestamp}"
    
    @classmethod
    def create_log(cls, request, action, object_type, object_id=None, diff=None):
        """
        Create audit log entry.
        """
        return cls.objects.create(
            tenant_id=getattr(request, 'tenant_id', None),
            actor_user_id=request.user.id if request.user.is_authenticated else None,
            action=action,
            object_type=object_type,
            object_id=object_id,
            diff=diff or {},
            ip=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
