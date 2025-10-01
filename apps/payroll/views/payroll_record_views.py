"""
PayrollRecord views.
"""
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from ..models import PayrollRecord
from ..serializers import PayrollRecordSerializer


class PayrollRecordViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing payroll records.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    ordering_fields = ['gross_pay', 'net_pay', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Get payroll records.
        """
        return PayrollRecord.objects.all().select_related('employee', 'payroll_period')
    
    def get_serializer_class(self):
        """
        Return appropriate serializer.
        """
        return PayrollRecordSerializer
