"""
PayrollComponent model.
"""
from django.db import models
from apps.core.models import BaseModel


class PayrollComponent(BaseModel):
    """
    Payroll components (allowances, deductions, etc.)
    """
    COMPONENT_TYPES = [
        ('earning', 'Earning'),
        ('deduction', 'Deduction'),
    ]
    
    CALCULATION_METHODS = [
        ('fixed', 'Fixed Amount'),
        ('percentage', 'Percentage of Basic'),
        ('formula', 'Custom Formula'),
    ]
    
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    component_type = models.CharField(max_length=20, choices=COMPONENT_TYPES)
    calculation_method = models.CharField(max_length=20, choices=CALCULATION_METHODS)
    
    # Configuration
    is_taxable = models.BooleanField(default=True)
    is_mandatory = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Calculation values
    fixed_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    percentage_value = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    formula = models.TextField(blank=True)
    
    class Meta:
        db_table = 'payroll_components'
        unique_together = [('code',)]
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['component_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})"
