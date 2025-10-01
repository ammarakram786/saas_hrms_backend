"""
Shift model.
"""
from django.db import models
from apps.core.models import BaseModel


class Shift(BaseModel):
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
            models.Index(fields=['name']),
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
