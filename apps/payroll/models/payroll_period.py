"""
PayrollPeriod model.
"""
from django.db import models
from apps.core.models import BaseModel


class PayrollPeriod(BaseModel):
    """
    Payroll processing period.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    name = models.CharField(max_length=100)
    period_start = models.DateField()
    period_end = models.DateField()
    pay_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Processing details
    processed_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'payroll_periods'
        ordering = ['-period_start']
        unique_together = [('period_start', 'period_end')]
    
    def __str__(self):
        return f"{self.name} ({self.period_start} - {self.period_end})"
