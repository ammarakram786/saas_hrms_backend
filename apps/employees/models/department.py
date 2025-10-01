"""
Department model.
"""
from django.db import models
from apps.core.models import BaseModel


class Department(BaseModel):
    """
    Model for managing departments.
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    
    # Department hierarchy
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sub_departments'
    )
    
    # Department head
    head = models.ForeignKey(
        'Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_departments'
    )
    
    # Budget and cost center
    budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    cost_center = models.CharField(max_length=20, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'departments'
        ordering = ['name']
        unique_together = [('code',)]
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
            models.Index(fields=['parent']),
        ]
    
    def __str__(self):
        return self.name
    
    @property
    def employee_count(self):
        """Get number of employees in this department."""
        return self.employees.filter(status='active').count()

    def get_all_employees(self):
        """Get all employees in this department and sub-departments."""
        departments = [self]

        # Get all sub-departments recursively
        def collect_subdepts(dept):
            for sub_dept in dept.sub_departments.filter(is_active=True):
                departments.append(sub_dept)
                collect_subdepts(sub_dept)

        collect_subdepts(self)

        # Get all employees from all departments in the hierarchy
        from .employee import Employee
        return Employee.objects.filter(
            department__in=departments,
            status='active'
        ).select_related('manager', 'user')
