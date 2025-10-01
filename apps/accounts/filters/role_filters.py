"""
Role filters.
"""
import django_filters
from django.db.models import Q
from ..models import Role


class RoleFilter(django_filters.FilterSet):
    """
    Filter for Role model.
    """
    # Text search
    search = django_filters.CharFilter(method='filter_search')
    
    # Permission filters
    has_permissions = django_filters.BooleanFilter(field_name='permissions', lookup_expr='isnull', exclude=True)
    permission_name = django_filters.CharFilter(field_name='permissions__name', lookup_expr='icontains')
    
    # Ordering
    ordering = django_filters.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('created_at', 'created_at'),
        ),
        field_labels={
            'name': 'Name',
            'created_at': 'Created Date',
        }
    )
    
    class Meta:
        model = Role
        fields = {
            'name': ['exact', 'icontains'],
            'description': ['icontains'],
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
