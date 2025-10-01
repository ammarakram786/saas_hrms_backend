"""
Department filters.
"""
import django_filters
from django.db.models import Q
from ..models import Department


class DepartmentFilter(django_filters.FilterSet):
    """
    Filter for Department model.
    """
    # Text search
    search = django_filters.CharFilter(method='filter_search')
    
    # Status filter
    is_active = django_filters.BooleanFilter()
    
    # Parent department
    parent = django_filters.ModelChoiceFilter(queryset=Department.objects.all())
    has_parent = django_filters.BooleanFilter(field_name='parent', lookup_expr='isnull', exclude=True)
    
    # Budget filters
    budget_min = django_filters.NumberFilter(field_name='budget', lookup_expr='gte')
    budget_max = django_filters.NumberFilter(field_name='budget', lookup_expr='lte')
    
    # Ordering
    ordering = django_filters.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('code', 'code'),
            ('budget', 'budget'),
            ('created_at', 'created_at'),
        ),
        field_labels={
            'name': 'Name',
            'code': 'Code',
            'budget': 'Budget',
            'created_at': 'Created Date',
        }
    )
    
    class Meta:
        model = Department
        fields = {
            'name': ['exact', 'icontains'],
            'code': ['exact', 'icontains'],
            'cost_center': ['exact', 'icontains'],
        }
    
    def filter_search(self, queryset, name, value):
        """
        Search across multiple fields.
        """
        if not value:
            return queryset
        
        return queryset.filter(
            Q(name__icontains=value) |
            Q(code__icontains=value) |
            Q(description__icontains=value) |
            Q(cost_center__icontains=value)
        )
