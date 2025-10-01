"""
Attendance filters.
"""
import django_filters
from django.db.models import Q
from ..models import AttendanceRecord


class AttendanceFilter(django_filters.FilterSet):
    """
    Filter for AttendanceRecord model.
    """
    # Text search
    search = django_filters.CharFilter(method='filter_search')
    
    # Status filter
    status = django_filters.ChoiceFilter(choices=AttendanceRecord.STATUS_CHOICES)
    
    # Date filters
    date_from = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='date', lookup_expr='lte')
    
    # Time filters
    check_in_from = django_filters.DateTimeFilter(field_name='check_in', lookup_expr='gte')
    check_in_to = django_filters.DateTimeFilter(field_name='check_in', lookup_expr='lte')
    check_out_from = django_filters.DateTimeFilter(field_name='check_out', lookup_expr='gte')
    check_out_to = django_filters.DateTimeFilter(field_name='check_out', lookup_expr='lte')
    
    # Hours filters
    hours_worked_min = django_filters.NumberFilter(field_name='hours_worked', lookup_expr='gte')
    hours_worked_max = django_filters.NumberFilter(field_name='hours_worked', lookup_expr='lte')
    
    # Manual entry filter
    is_manual_entry = django_filters.BooleanFilter()
    
    # Employee filters
    employee = django_filters.ModelChoiceFilter(queryset=None)  # Will be set in view
    department = django_filters.CharFilter(field_name='employee__department', lookup_expr='icontains')
    
    # Ordering
    ordering = django_filters.OrderingFilter(
        fields=(
            ('date', 'date'),
            ('check_in', 'check_in'),
            ('hours_worked', 'hours_worked'),
            ('created_at', 'created_at'),
        ),
        field_labels={
            'date': 'Date',
            'check_in': 'Check In Time',
            'hours_worked': 'Hours Worked',
            'created_at': 'Created Date',
        }
    )
    
    class Meta:
        model = AttendanceRecord
        fields = {
            'shift': ['exact', 'icontains'],
            'leave_type': ['exact', 'icontains'],
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
            Q(notes__icontains=value) |
            Q(shift__icontains=value)
        )
