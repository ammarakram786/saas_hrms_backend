"""
AuditLog model.
"""
from django.db import models
from django.db.models import JSONField
from apps.core.models import BaseModel


class AuditLog(BaseModel):
    """
    Audit log for tracking changes to models.
    """
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
        ('login', 'Login'),
        ('logout', 'Logout'),
    ]
    
    # Actor information
    actor_user_id = models.UUIDField(null=True, blank=True)
    actor_username = models.CharField(max_length=150, blank=True)
    actor_ip = models.GenericIPAddressField(null=True, blank=True)
    actor_user_agent = models.TextField(blank=True)
    
    # Action details
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100, blank=True)
    
    # Change details
    old_values = JSONField(default=dict, blank=True)
    new_values = JSONField(default=dict, blank=True)
    changed_fields = JSONField(default=list, blank=True)
    
    # Additional context
    description = models.TextField(blank=True)
    metadata = JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['actor_user_id']),
            models.Index(fields=['action']),
            models.Index(fields=['model_name']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.action} {self.model_name} by {self.actor_username}"
    
    @classmethod
    def create_log(cls, actor_user, action, model_name, object_id=None, 
                   old_values=None, new_values=None, description=None, **kwargs):
        """
        Create an audit log entry.
        """
        return cls.objects.create(
            actor_user_id=actor_user.id if actor_user else None,
            actor_username=actor_user.username if actor_user else 'System',
            action=action,
            model_name=model_name,
            object_id=str(object_id) if object_id else '',
            old_values=old_values or {},
            new_values=new_values or {},
            description=description or '',
            **kwargs
        )
