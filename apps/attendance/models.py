"""
Attendance and leave management models.
"""
from django.db import models
from django.db.models import JSONField
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from apps.core.models import TenantAwareModel


class AttendanceRecord(TenantAwareModel):
    """
    Daily attendance record for employees.
    """
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('half_day', 'Half Day'),
        ('on_leave', 'On Leave'),
        ('holiday', 'Holiday'),
        ('weekend', 'Weekend'),
    ]
    
    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )
    
    date = models.DateField()
    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)
    
    # Break times
    break_start = models.DateTimeField(null=True, blank=True)
    break_end = models.DateTimeField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    shift = models.CharField(max_length=50, default='regular')
    
    # Calculated fields
    hours_worked = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True
    )
    overtime_hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0
    )
    
    # Leave details if on leave
    leave_type = models.CharField(max_length=50, blank=True)
    leave_request = models.ForeignKey(
        'LeaveRequest',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Notes and manual adjustments
    notes = models.TextField(blank=True)
    is_manual_entry = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_attendance'
    )
    
    class Meta:
        db_table = 'attendance'
        ordering = ['-date']
        unique_together = [('tenant_id', 'employee', 'date')]
        indexes = [
            models.Index(fields=['tenant_id', 'employee', 'date']),
            models.Index(fields=['tenant_id', 'date']),
            models.Index(fields=['tenant_id', 'status']),
            models.Index(fields=['check_in']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.date} ({self.status})"
    
    def calculate_hours_worked(self):
        """
        Calculate hours worked based on check-in/out times.
        """
        if not self.check_in or not self.check_out:
            return None
        
        # Calculate total time
        total_time = self.check_out - self.check_in
        
        # Subtract break time if applicable
        if self.break_start and self.break_end:
            break_time = self.break_end - self.break_start
            total_time -= break_time
        
        # Convert to hours
        hours = total_time.total_seconds() / 3600
        return round(hours, 2)
    
    def calculate_overtime(self, standard_hours=8):
        """
        Calculate overtime hours.
        """
        if not self.hours_worked:
            return 0
        
        if self.hours_worked > standard_hours:
            return round(self.hours_worked - standard_hours, 2)
        
        return 0
    
    def save(self, *args, **kwargs):
        """
        Calculate hours on save.
        """
        if self.check_in and self.check_out:
            self.hours_worked = self.calculate_hours_worked()
            self.overtime_hours = self.calculate_overtime()
        
        super().save(*args, **kwargs)
    
    def is_late(self, shift_start_time="09:00"):
        """
        Check if employee was late.
        """
        if not self.check_in:
            return False
        
        from datetime import time
        shift_start = datetime.combine(
            self.date,
            time.fromisoformat(shift_start_time)
        )
        
        return self.check_in > shift_start


class LeaveType(TenantAwareModel):
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
        unique_together = [('tenant_id', 'code')]
        indexes = [
            models.Index(fields=['tenant_id', 'code']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name


class LeaveBalance(TenantAwareModel):
    """
    Leave balance for employees.
    """
    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='leave_balances'
    )
    leave_type = models.ForeignKey(
        LeaveType,
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
        unique_together = [('tenant_id', 'employee', 'leave_type', 'year')]
        indexes = [
            models.Index(fields=['tenant_id', 'employee', 'year']),
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


class LeaveRequest(TenantAwareModel):
    """
    Leave requests submitted by employees.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='leave_requests'
    )
    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.CASCADE
    )
    
    start_date = models.DateField()
    end_date = models.DateField()
    days_requested = models.DecimalField(max_digits=4, decimal_places=1)
    
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Approval workflow
    approved_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_leaves'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    
    # Supporting documents
    documents = JSONField(default=list, blank=True)
    
    class Meta:
        db_table = 'leave_requests'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant_id', 'employee']),
            models.Index(fields=['tenant_id', 'status']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['leave_type']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.leave_type.name} ({self.start_date} to {self.end_date})"
    
    def clean(self):
        """
        Validate leave request.
        """
        if self.start_date > self.end_date:
            raise ValidationError("Start date cannot be after end date.")
        
        # Check for overlapping requests
        overlapping = LeaveRequest.objects.filter(
            tenant_id=self.tenant_id,
            employee=self.employee,
            status__in=['pending', 'approved']
        ).filter(
            models.Q(start_date__lte=self.end_date) &
            models.Q(end_date__gte=self.start_date)
        )
        
        if self.pk:
            overlapping = overlapping.exclude(pk=self.pk)
        
        if overlapping.exists():
            raise ValidationError("Leave request overlaps with existing request.")
    
    def calculate_days(self):
        """
        Calculate number of leave days (excluding weekends).
        """
        from datetime import timedelta
        
        current_date = self.start_date
        days = 0
        
        while current_date <= self.end_date:
            # Skip weekends (assuming Saturday=5, Sunday=6)
            if current_date.weekday() < 5:  # Monday=0, Friday=4
                days += 1
            current_date += timedelta(days=1)
        
        return days
    
    def approve(self, approved_by_user):
        """
        Approve the leave request.
        """
        if self.status != 'pending':
            raise ValidationError("Can only approve pending requests.")
        
        # Check leave balance
        try:
            balance = LeaveBalance.objects.get(
                tenant_id=self.tenant_id,
                employee=self.employee,
                leave_type=self.leave_type,
                year=self.start_date.year
            )
            
            if balance.available_days < self.days_requested:
                raise ValidationError("Insufficient leave balance.")
            
        except LeaveBalance.DoesNotExist:
            raise ValidationError("Leave balance not found.")
        
        # Update status
        self.status = 'approved'
        self.approved_by = approved_by_user
        self.approved_at = datetime.now()
        self.save()
        
        # Update leave balance
        balance.used_days += self.days_requested
        balance.save()
        
        # Create attendance records
        self._create_attendance_records()
    
    def reject(self, approved_by_user, reason):
        """
        Reject the leave request.
        """
        if self.status != 'pending':
            raise ValidationError("Can only reject pending requests.")
        
        self.status = 'rejected'
        self.approved_by = approved_by_user
        self.approved_at = datetime.now()
        self.rejection_reason = reason
        self.save()
    
    def _create_attendance_records(self):
        """
        Create attendance records for approved leave.
        """
        current_date = self.start_date
        
        while current_date <= self.end_date:
            if current_date.weekday() < 5:  # Skip weekends
                AttendanceRecord.objects.update_or_create(
                    tenant_id=self.tenant_id,
                    employee=self.employee,
                    date=current_date,
                    defaults={
                        'status': 'on_leave',
                        'leave_type': self.leave_type.name,
                        'leave_request': self
                    }
                )
            
            current_date += timedelta(days=1)
    
    def save(self, *args, **kwargs):
        """
        Calculate days on save.
        """
        if not self.days_requested:
            self.days_requested = self.calculate_days()
        
        super().save(*args, **kwargs)


class Shift(TenantAwareModel):
    """
    Work shifts configuration.
    """
    name = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    break_duration = models.IntegerField(default=60)  # minutes
    
    # Shift settings
    is_overnight = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Grace periods
    late_grace_period = models.IntegerField(default=15)  # minutes
    early_checkout_grace_period = models.IntegerField(default=15)  # minutes
    
    class Meta:
        db_table = 'shifts'
        ordering = ['start_time']
        indexes = [
            models.Index(fields=['tenant_id', 'name']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.start_time} - {self.end_time})"
    
    @property
    def duration_hours(self):
        """Calculate shift duration in hours."""
        from datetime import datetime, timedelta
        
        start = datetime.combine(datetime.min, self.start_time)
        end = datetime.combine(datetime.min, self.end_time)
        
        if self.is_overnight and end <= start:
            end += timedelta(days=1)
        
        duration = end - start - timedelta(minutes=self.break_duration)
        return duration.total_seconds() / 3600


class Holiday(TenantAwareModel):
    """
    Company holidays.
    """
    name = models.CharField(max_length=200)
    date = models.DateField()
    is_optional = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'holidays'
        ordering = ['date']
        unique_together = [('tenant_id', 'date', 'name')]
        indexes = [
            models.Index(fields=['tenant_id', 'date']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.date}"
