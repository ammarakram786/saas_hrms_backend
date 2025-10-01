"""
Holiday model.
"""
from django.db import models
from apps.core.models import BaseModel


class Holiday(BaseModel):
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
        unique_together = [('date', 'name')]
        indexes = [
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.date}"
