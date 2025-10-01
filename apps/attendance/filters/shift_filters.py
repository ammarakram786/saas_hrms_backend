"""
Shift filters.
"""
import django_filters
from django.db.models import Q
from ..models import Shift


class ShiftFilter(django_filters.FilterSet):
    """
    Filter for Shift model.
    """
    # Text search
    search = django_filters.CharFilter(method='filter_search')
    
    # Status filter
    is_active = django_filters.BooleanFilter()
    is_overnight = django_filters.BooleanFilter()
    
    # Time filters
    start_time_from = django_filters.TimeFilter(field_name='start_time', lookup_expr='gte')
    start_time_to = django_filters.TimeFilter(field_name='start_time', lookup_expr='lte')
    end_time_from = django_filters.TimeFilter(field_name='end_time', lookup_expr='gte')
    end_time_to = django_filters.TimeFilter(field_name='end_time', lookup_expr='lte')
    
    # Duration filters
    duration_hours_min = django_filters.NumberFilter(field_name='duration_hours', lookup_expr='gte')
    duration_hours_max = django_filters.NumberFilter(field_name='duration_hours', lookup_expr='lte')
    
    # Ordering
    ordering = django_filters.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('start_time', 'start_time'),
            ('duration_hours', 'duration_hours'),
            ('created_at', 'created_at'),
        ),
        field_labels={
            'name': 'Name',
            'start_time': 'Start Time',
            'duration_hours': 'Duration Hours',
            'created_at': 'Created Date',
        }
    )
    
    class Meta:
        model = Shift
        fields = {
            'name': ['exact', 'icontains'],
        }
    
    def filter_search(self, queryset, name, value):
        """
        Search across multiple fields.
        """
        if not value:
            return queryset
        
        return queryset.filter(
            Q(name__icontains=value)
        )
