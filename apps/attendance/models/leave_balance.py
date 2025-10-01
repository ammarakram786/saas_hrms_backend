"""
LeaveBalance model.
"""
from django.db import models
from apps.core.models import BaseModel


class LeaveBalance(BaseModel):
    """
    Leave balance for employees.
    """
    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='leave_balances'
    )
    leave_type = models.ForeignKey(
        'LeaveType',
        on_delete=models.CASCADE
    )
    year = models.IntegerField()
    
    # Balance tracking
    allocated_days = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    used_days = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    pending_days = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    carried_forward = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    
    class Meta:
        db_table = 'leave_balances'
        ordering = ['-year']
        unique_together = [('employee', 'leave_type', 'year')]
        indexes = [
            models.Index(fields=['employee', 'year']),
            models.Index(fields=['leave_type']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.leave_type.name} ({self.year})"
    
    @property
    def available_days(self):
        """Calculate available leave days."""
        return self.allocated_days + self.carried_forward - self.used_days - self.pending_days
    
    @property
    def total_allocated(self):
        """Total allocated days including carried forward."""
        return self.allocated_days + self.carried_forward
