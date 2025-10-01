"""
User filters.
"""
import django_filters
from django.db.models import Q
from ..models import User


class UserFilter(django_filters.FilterSet):
    """
    Filter for User model.
    """
    # Text search
    search = django_filters.CharFilter(method='filter_search')
    
    # Status filters
    is_active = django_filters.BooleanFilter()
    is_staff = django_filters.BooleanFilter()
    is_superuser = django_filters.BooleanFilter()
    
    # Date filters
    created_at_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    last_login_from = django_filters.DateTimeFilter(field_name='last_login', lookup_expr='gte')
    last_login_to = django_filters.DateTimeFilter(field_name='last_login', lookup_expr='lte')
    
    # Role filters
    has_roles = django_filters.BooleanFilter(field_name='roles', lookup_expr='isnull', exclude=True)
    role_name = django_filters.CharFilter(field_name='roles__name', lookup_expr='icontains')
    
    # Ordering
    ordering = django_filters.OrderingFilter(
        fields=(
            ('first_name', 'first_name'),
            ('last_name', 'last_name'),
            ('email', 'email'),
            ('created_at', 'created_at'),
            ('last_login', 'last_login'),
        ),
        field_labels={
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'Email',
            'created_at': 'Created Date',
            'last_login': 'Last Login',
        }
    )
    
    class Meta:
        model = User
        fields = {
            'email': ['exact', 'icontains'],
            'first_name': ['exact', 'icontains'],
            'last_name': ['exact', 'icontains'],
        }
    
    def filter_search(self, queryset, name, value):
        """
        Search across multiple fields.
        """
        if not value:
            return queryset
        
        return queryset.filter(
            Q(first_name__icontains=value) |
            Q(last_name__icontains=value) |
            Q(email__icontains=value)
        )
