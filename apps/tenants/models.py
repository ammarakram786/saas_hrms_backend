"""
Tenant models for multi-tenant SaaS functionality.
"""
import uuid
from django.db import models
from django.db.models import JSONField
from apps.core.models import BaseModel


class SubscriptionPlan(BaseModel):
    """
    Subscription plan definitions.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_users = models.IntegerField(default=10)
    max_employees = models.IntegerField(default=50)
    features = JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'subscription_plans'
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name


class Tenant(BaseModel):
    """
    Represents a tenant (company) in the multi-tenant system.
    """
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('pending', 'Pending'),
    ]
    
    SUBSCRIPTION_STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('cancelled', 'Cancelled'),
        ('past_due', 'Past Due'),
        ('trialing', 'Trialing'),
        ('paused', 'Paused'),
    ]
    
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    domain = models.CharField(max_length=255, null=True, blank=True)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    settings = JSONField(default=dict, blank=True)
    created_by = models.UUIDField(null=True, blank=True)  # Reference to superuser who created the tenant
    max_users = models.IntegerField(default=10)
    max_employees = models.IntegerField(default=50)
    
    # Subscription related fields
    subscription_plan = models.ForeignKey(
        SubscriptionPlan, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='tenants'
    )
    subscription_id = models.CharField(max_length=255, null=True, blank=True)
    subscription_status = models.CharField(
        max_length=50, 
        choices=SUBSCRIPTION_STATUS_CHOICES, 
        null=True, 
        blank=True
    )
    subscription_start_date = models.DateTimeField(null=True, blank=True)
    subscription_end_date = models.DateTimeField(null=True, blank=True)
    trial_end_date = models.DateTimeField(null=True, blank=True)
    
    # Billing information
    billing_email = models.EmailField(null=True, blank=True)
    billing_address = models.TextField(null=True, blank=True)
    tax_id = models.CharField(max_length=50, null=True, blank=True)
    
    # Contact information
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'tenants'
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status']),
            models.Index(fields=['plan']),
            models.Index(fields=['subscription_status']),
        ]
    
    def __str__(self):
        return self.name
    
    @property
    def is_active(self):
        """Check if tenant is active."""
        return self.status == 'active'
    
    @property
    def current_user_count(self):
        """Get current number of users in this tenant."""
        try:
            from apps.accounts.models import User
            return User.objects.filter(tenant_id=self.id, is_active=True).count()
        except ImportError:
            return 0
    
    @property
    def current_employee_count(self):
        """Get current number of employees in this tenant."""
        try:
            from apps.employees.models import Employee
            return Employee.objects.filter(tenant_id=self.id, end_date__isnull=True).count()
        except ImportError:
            return 0
    
    def can_add_user(self):
        """Check if tenant can add more users."""
        return self.current_user_count < self.max_users
    
    def can_add_employee(self):
        """Check if tenant can add more employees."""
        return self.current_employee_count < self.max_employees
    
    def get_default_settings(self):
        """Get default tenant settings."""
        return {
            'timezone': 'UTC',
            'date_format': 'YYYY-MM-DD',
            'currency': 'USD',
            'working_hours': {
                'start': '09:00',
                'end': '17:00',
                'break_duration': 60,  # minutes
            },
            'leave_policy': {
                'annual_leave_days': 20,
                'sick_leave_days': 10,
                'casual_leave_days': 5,
            },
            'payroll_settings': {
                'pay_frequency': 'monthly',
                'pay_day': 30,  # day of month
                'tax_settings': {},
            },
            'notification_settings': {
                'email_notifications': True,
                'sms_notifications': False,
            },
            'features': {
                'time_tracking': True,
                'leave_management': True,
                'payroll': True,
                'performance_reviews': False,
                'document_management': False,
            }
        }
    
    def initialize_settings(self):
        """Initialize tenant with default settings."""
        if not self.settings:
            self.settings = self.get_default_settings()
            self.save()
    
    def update_setting(self, key, value):
        """Update a specific setting."""
        if not self.settings:
            self.settings = self.get_default_settings()
        
        # Support nested key updates like 'working_hours.start'
        keys = key.split('.')
        current = self.settings
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value
        
        self.save()
    
    def get_setting(self, key, default=None):
        """Get a specific setting value."""
        if not self.settings:
            return default
        
        # Support nested key access like 'working_hours.start'
        keys = key.split('.')
        current = self.settings
        try:
            for k in keys:
                current = current[k]
            return current
        except (KeyError, TypeError):
            return default


class SubscriptionHistory(BaseModel):
    """
    Track subscription changes and billing history.
    """
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='subscription_history')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50)  # created, upgraded, downgraded, cancelled, renewed
    old_plan = models.CharField(max_length=50, null=True, blank=True)
    new_plan = models.CharField(max_length=50, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    billing_period = models.CharField(max_length=20, null=True, blank=True)  # monthly, yearly
    notes = models.TextField(blank=True)
    metadata = JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'subscription_history'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.tenant.name} - {self.action} - {self.created_at.strftime('%Y-%m-%d')}"