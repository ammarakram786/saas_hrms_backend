"""
PayrollPeriod views.
"""
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from ..models import PayrollPeriod
from ..serializers import PayrollPeriodSerializer


class PayrollPeriodViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing payroll periods.
    """
    permission_classes = [IsAuthenticated]
    def get_filter_backends(self):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['period_start', 'period_end', 'pay_date']
    ordering = ['-period_start']
    
    def get_queryset(self):
        """
        Get payroll periods.
        """
        return PayrollPeriod.objects.all().select_related('processed_by')
    
    def get_serializer_class(self):
        """
        Return appropriate serializer.
        """
        return PayrollPeriodSerializer
