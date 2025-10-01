"""
EmployeeDocument serializers.
"""
from rest_framework import serializers
from ..models import EmployeeDocument


class EmployeeDocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for EmployeeDocument model.
    """
    uploaded_by_name = serializers.CharField(source='uploaded_by.full_name', read_only=True)
    
    class Meta:
        model = EmployeeDocument
        fields = [
            'id', 'name', 'document_type', 'file_path', 'file_size',
            'mime_type', 'is_confidential', 'uploaded_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uploaded_by_name', 'created_at', 'updated_at']
