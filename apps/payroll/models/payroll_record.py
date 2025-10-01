"""
PayrollRecord model.
"""
from django.db import models
from django.db.models import JSONField
from apps.core.models import BaseModel


class PayrollRecord(BaseModel):
    """
    Individual employee payroll record.
    """
    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='payroll_records'
    )
    payroll_period = models.ForeignKey(
        'PayrollPeriod',
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
        unique_together = [('employee', 'payroll_period')]
        indexes = [
            models.Index(fields=['employee']),
            models.Index(fields=['payroll_period']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.payroll_period.name}"
    
    def calculate_totals(self):
        """Calculate payroll totals."""
        self.gross_pay = self.base_salary + self.overtime_pay + self.allowances + self.bonuses
        self.total_deductions = self.tax + self.social_security + self.other_deductions
        self.net_pay = self.gross_pay - self.total_deductions
        self.save()
