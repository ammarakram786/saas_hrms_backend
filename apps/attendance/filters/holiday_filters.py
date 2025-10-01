"""
Holiday filters.
"""
import django_filters
from django.db.models import Q
from ..models import Holiday


class HolidayFilter(django_filters.FilterSet):
    """
    Filter for Holiday model.
    """
    # Text search
    search = django_filters.CharFilter(method='filter_search')
    
    # Date filters
    date_from = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='date', lookup_expr='lte')
    
    # Year filter
    year = django_filters.NumberFilter(field_name='date__year')
    
    # Month filter
    month = django_filters.NumberFilter(field_name='date__month')
    
    # Optional filter
    is_optional = django_filters.BooleanFilter()
    
    # Ordering
    ordering = django_filters.OrderingFilter(
        fields=(
            ('date', 'date'),
            ('name', 'name'),
            ('created_at', 'created_at'),
        ),
        field_labels={
            'date': 'Date',
            'name': 'Name',
            'created_at': 'Created Date',
        }
    )
    
    class Meta:
        model = Holiday
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
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )
