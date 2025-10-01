"""
EmployeeDocument views.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..models import EmployeeDocument
from ..serializers import EmployeeDocumentSerializer


class EmployeeDocumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing employee documents.
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Get employee documents.
        """
        return EmployeeDocument.objects.all().select_related('employee', 'uploaded_by')
    
    def get_serializer_class(self):
        """
        Return appropriate serializer.
        """
        return EmployeeDocumentSerializer
    
    def perform_create(self, serializer):
        """
        Set uploaded_by to current user.
        """
        serializer.save(uploaded_by=self.request.user)
