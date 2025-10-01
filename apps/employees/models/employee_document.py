"""
EmployeeDocument model.
"""
from django.db import models
from apps.core.models import BaseModel


class EmployeeDocument(BaseModel):
    """
    Model for storing employee documents.
    """
    DOCUMENT_TYPES = [
        ('id', 'ID Document'),
        ('contract', 'Employment Contract'),
        ('resume', 'Resume/CV'),
        ('certificate', 'Certificate'),
        ('photo', 'Photo'),
        ('tax_form', 'Tax Form'),
        ('bank_details', 'Bank Details'),
        ('emergency_contact', 'Emergency Contact'),
        ('other', 'Other'),
    ]
    
    employee = models.ForeignKey(
        'Employee',
        on_delete=models.CASCADE,
        related_name='employee_documents'
    )
    
    name = models.CharField(max_length=255)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    file_path = models.CharField(max_length=500)
    file_size = models.IntegerField()
    mime_type = models.CharField(max_length=100)
    
    # Access control
    is_confidential = models.BooleanField(default=False)
    uploaded_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True
    )
    
    class Meta:
        db_table = 'employee_documents'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['employee']),
            models.Index(fields=['document_type']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.employee.full_name}"
