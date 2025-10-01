"""
Employee model.
"""
from django.db import models
from django.db.models import JSONField
from apps.core.models import BaseModel


class Employee(BaseModel):
    """
    Employee model for storing employee information.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('terminated', 'Terminated'),
        ('on_leave', 'On Leave'),
    ]
    
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('intern', 'Intern'),
        ('temporary', 'Temporary'),
    ]
    
    # Link to user account (optional - not all employees need login access)
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employee_profile'
    )
    
    # Personal Information
    employee_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, blank=True)
    marital_status = models.CharField(max_length=20, blank=True)
    nationality = models.CharField(max_length=50, blank=True)
    
    # Address Information
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Employment Information
    department = models.ForeignKey(
        'Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees'
    )
    position = models.CharField(max_length=100)
    employment_type = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_TYPE_CHOICES,
        default='full_time'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    
    # Dates
    hire_date = models.DateField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    probation_end_date = models.DateField(null=True, blank=True)
    
    # Salary Information
    base_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    currency = models.CharField(max_length=3, default='USD')
    pay_frequency = models.CharField(
        max_length=20,
        choices=[
            ('weekly', 'Weekly'),
            ('bi_weekly', 'Bi-weekly'),
            ('monthly', 'Monthly'),
            ('annual', 'Annual'),
        ],
        default='monthly'
    )
    
    # Manager/Reporting
    manager = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='direct_reports'
    )
    
    # Additional Information
    emergency_contact = JSONField(default=dict, blank=True)
    skills = JSONField(default=list, blank=True)
    certifications = JSONField(default=list, blank=True)
    documents_data = JSONField(default=list, blank=True)
    
    # Metadata for custom fields
    metadata = JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'employees'
        ordering = ['last_name', 'first_name']
        unique_together = [('employee_id',)]
        indexes = [
            models.Index(fields=['employee_id']),
            models.Index(fields=['department']),
            models.Index(fields=['status']),
            models.Index(fields=['manager']),
            models.Index(fields=['email']),
            models.Index(fields=['hire_date']),
            models.Index(fields=['position']),
            models.Index(fields=['employment_type']),
            # Composite indexes for common queries
            models.Index(fields=['department', 'status']),
            models.Index(fields=['manager', 'status']),
            models.Index(fields=['hire_date', 'status']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"
    
    @property
    def full_name(self):
        """Get employee's full name."""
        middle = f" {self.middle_name}" if self.middle_name else ""
        return f"{self.first_name}{middle} {self.last_name}".strip()
    
    @property
    def is_active(self):
        """Check if employee is active."""
        return self.status == 'active'
    
    @property
    def years_of_service(self):
        """Calculate years of service."""
        from datetime import date
        end_date = self.end_date or date.today()
        delta = end_date - self.start_date
        return round(delta.days / 365.25, 1)
    
    @property
    def is_on_probation(self):
        """Check if employee is still on probation."""
        if not self.probation_end_date:
            return False
        from datetime import date
        return date.today() <= self.probation_end_date
    
    def get_direct_reports(self):
        """Get employees reporting to this employee."""
        return Employee.objects.filter(
            manager=self,
            status='active'
        )
    
    def get_org_hierarchy(self):
        """Get organizational hierarchy path."""
        hierarchy = [self]
        current = self.manager
        
        while current:
            hierarchy.append(current)
            current = current.manager
            # Prevent infinite loops
            if current in hierarchy:
                break
        
        return list(reversed(hierarchy))
    
    def terminate(self, end_date=None, reason=None):
        """Terminate employee."""
        from datetime import date
        
        self.status = 'terminated'
        self.end_date = end_date or date.today()
        
        if reason:
            if 'termination' not in self.metadata:
                self.metadata['termination'] = {}
            self.metadata['termination']['reason'] = reason
            self.metadata['termination']['date'] = str(self.end_date)
        
        self.save()
        
        # Deactivate linked user account if exists
        if self.user:
            self.user.is_active = False
            self.user.save()
    
    def reactivate(self):
        """Reactivate terminated employee."""
        self.status = 'active'
        self.end_date = None
        
        # Remove termination metadata
        if 'termination' in self.metadata:
            del self.metadata['termination']
        
        self.save()
        
        # Reactivate linked user account if exists
        if self.user:
            self.user.is_active = True
            self.user.save()
