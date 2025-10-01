"""
LeaveRequest filters.
"""
import django_filters
from django.db.models import Q
from ..models import LeaveRequest


class LeaveRequestFilter(django_filters.FilterSet):
    """
    Filter for LeaveRequest model.
    """
    # Text search
    search = django_filters.CharFilter(method='filter_search')
    
    # Status filter
    status = django_filters.ChoiceFilter(choices=LeaveRequest.STATUS_CHOICES)
    
    # Date filters
    start_date_from = django_filters.DateFilter(field_name='start_date', lookup_expr='gte')
    start_date_to = django_filters.DateFilter(field_name='start_date', lookup_expr='lte')
    end_date_from = django_filters.DateFilter(field_name='end_date', lookup_expr='gte')
    end_date_to = django_filters.DateFilter(field_name='end_date', lookup_expr='lte')
    
    # Days filters
    days_requested_min = django_filters.NumberFilter(field_name='days_requested', lookup_expr='gte')
    days_requested_max = django_filters.NumberFilter(field_name='days_requested', lookup_expr='lte')
    
    # Employee filters
    employee = django_filters.ModelChoiceFilter(queryset=None)  # Will be set in view
    department = django_filters.CharFilter(field_name='employee__department', lookup_expr='icontains')
    
    # Leave type filter
    leave_type = django_filters.ModelChoiceFilter(queryset=None)  # Will be set in view
    
    # Approval filters
    approved_by = django_filters.ModelChoiceFilter(queryset=None)  # Will be set in view
    approved_at_from = django_filters.DateTimeFilter(field_name='approved_at', lookup_expr='gte')
    approved_at_to = django_filters.DateTimeFilter(field_name='approved_at', lookup_expr='lte')
    
    # Ordering
    ordering = django_filters.OrderingFilter(
        fields=(
            ('start_date', 'start_date'),
            ('end_date', 'end_date'),
            ('days_requested', 'days_requested'),
            ('created_at', 'created_at'),
        ),
        field_labels={
            'start_date': 'Start Date',
            'end_date': 'End Date',
            'days_requested': 'Days Requested',
            'created_at': 'Created Date',
        }
    )
    
    class Meta:
        model = LeaveRequest
        fields = {
            'reason': ['icontains'],
        }
    
    def filter_search(self, queryset, name, value):
        """
        Search across multiple fields.
        """
        if not value:
            return queryset
        
        return queryset.filter(
            Q(employee__first_name__icontains=value) |
            Q(employee__last_name__icontains=value) |
            Q(employee__employee_id__icontains=value) |
            Q(leave_type__name__icontains=value) |
            Q(reason__icontains=value)
        )
