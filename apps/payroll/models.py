"""
Payroll models.
"""
from django.db import models
from django.db.models import JSONField
from decimal import Decimal
from apps.core.models import TenantAwareModel


class PayrollPeriod(TenantAwareModel):
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
        unique_together = [('tenant_id', 'period_start', 'period_end')]


class PayrollRecord(TenantAwareModel):
    """
    Individual employee payroll record.
    """
    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='payroll_records'
    )
    payroll_period = models.ForeignKey(
        PayrollPeriod,
        on_delete=models.CASCADE,
        related_name='payroll_records'
    )
    
    # Salary components
    base_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    overtime_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bonuses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Deductions
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    social_security = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Calculated fields
    gross_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Detailed breakdown
    payslip_data = JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'payroll_records'
        unique_together = [('tenant_id', 'employee', 'payroll_period')]
    
    def calculate_totals(self):
        """Calculate payroll totals."""
        self.gross_pay = self.base_salary + self.overtime_pay + self.allowances + self.bonuses
        self.total_deductions = self.tax + self.social_security + self.other_deductions
        self.net_pay = self.gross_pay - self.total_deductions
        self.save()


class PayrollComponent(TenantAwareModel):
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
        unique_together = [('tenant_id', 'code')]
