"""
LeaveType model.
"""
from django.db import models
from apps.core.models import BaseModel


class LeaveType(BaseModel):
    """
    Types of leave available.
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    
    # Leave configuration
    days_allowed_per_year = models.IntegerField(default=0)
    is_paid = models.BooleanField(default=True)
    requires_approval = models.BooleanField(default=True)
    can_be_carried_forward = models.BooleanField(default=False)
    max_consecutive_days = models.IntegerField(null=True, blank=True)
    
    # Gender-specific leave
    applicable_gender = models.CharField(
        max_length=10,
        choices=[('all', 'All'), ('male', 'Male'), ('female', 'Female')],
        default='all'
    )
    
    # Active status
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'leave_types'
        ordering = ['name']
        unique_together = [('code',)]
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name
