"""
AttendanceRecord model.
"""
from django.db import models
from apps.core.models import BaseModel


class AttendanceRecord(BaseModel):
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
        unique_together = [('employee', 'date')]
        indexes = [
            models.Index(fields=['employee', 'date']),
            models.Index(fields=['date']),
            models.Index(fields=['status']),
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
