"""
LeaveBalance filters.
"""
import django_filters
from django.db.models import Q
from ..models import LeaveBalance


class LeaveBalanceFilter(django_filters.FilterSet):
    """
    Filter for LeaveBalance model.
    """
    # Text search
    search = django_filters.CharFilter(method='filter_search')
    
    # Year filter
    year = django_filters.NumberFilter()
    year_from = django_filters.NumberFilter(field_name='year', lookup_expr='gte')
    year_to = django_filters.NumberFilter(field_name='year', lookup_expr='lte')
    
    # Employee filters
    employee = django_filters.ModelChoiceFilter(queryset=None)  # Will be set in view
    department = django_filters.CharFilter(field_name='employee__department', lookup_expr='icontains')
    
    # Leave type filter
    leave_type = django_filters.ModelChoiceFilter(queryset=None)  # Will be set in view
    
    # Balance filters
    available_days_min = django_filters.NumberFilter(field_name='available_days', lookup_expr='gte')
    available_days_max = django_filters.NumberFilter(field_name='available_days', lookup_expr='lte')
    
    # Ordering
    ordering = django_filters.OrderingFilter(
        fields=(
            ('year', 'year'),
            ('available_days', 'available_days'),
            ('created_at', 'created_at'),
        ),
        field_labels={
            'year': 'Year',
            'available_days': 'Available Days',
            'created_at': 'Created Date',
        }
    )
    
    class Meta:
        model = LeaveBalance
        fields = {}
    
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
            Q(leave_type__name__icontains=value)
        )
