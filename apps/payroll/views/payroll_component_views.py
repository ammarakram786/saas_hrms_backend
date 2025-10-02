"""
PayrollComponent views.
"""
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from ..models import PayrollComponent
from ..serializers import PayrollComponentSerializer


class PayrollComponentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing payroll components.
    """
    permission_classes = [IsAuthenticated]
    def get_filter_backends(self):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code', 'component_type']
    ordering = ['name']
    
    def get_queryset(self):
        """
        Get payroll components.
        """
        return PayrollComponent.objects.all()
    
    def get_serializer_class(self):
        """
        Return appropriate serializer.
        """
        return PayrollComponentSerializer
