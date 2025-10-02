"""
LeaveBalance views.
"""
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from ..models import LeaveBalance
from ..serializers import LeaveBalanceSerializer
from ..filters import LeaveBalanceFilter


class LeaveBalanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing leave balances.
    """
    permission_classes = [IsAuthenticated]
    def get_filter_backends(self):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = LeaveBalanceFilter
    search_fields = ['employee__first_name', 'employee__last_name', 'leave_type__name']
    ordering_fields = ['year', 'available_days', 'allocated_days']
    ordering = ['-year', 'employee__last_name']
    
    def get_queryset(self):
        """
        Get leave balances.
        """
        return LeaveBalance.objects.all().select_related('employee', 'leave_type')
    
    def get_serializer_class(self):
        """
        Return appropriate serializer.
        """
        return LeaveBalanceSerializer
