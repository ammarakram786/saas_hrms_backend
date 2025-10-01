"""
LeaveRequest model.
"""
from django.db import models
from django.db.models import JSONField
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from apps.core.models import BaseModel


class LeaveRequest(BaseModel):
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
        'LeaveType',
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
            models.Index(fields=['employee']),
            models.Index(fields=['status']),
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
            from .leave_balance import LeaveBalance
            balance = LeaveBalance.objects.get(
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
        from .attendance_record import AttendanceRecord
        current_date = self.start_date
        
        while current_date <= self.end_date:
            if current_date.weekday() < 5:  # Skip weekends
                AttendanceRecord.objects.update_or_create(
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
