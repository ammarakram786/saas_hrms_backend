"""
Invitation filters.
"""
import django_filters
from django.db.models import Q
from ..models import Invitation


class InvitationFilter(django_filters.FilterSet):
    """
    Filter for Invitation model.
    """
    # Text search
    search = django_filters.CharFilter(method='filter_search')
    
    # Status filter
    status = django_filters.ChoiceFilter(choices=Invitation.STATUS_CHOICES)
    
    # Date filters
    created_at_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    expires_at_from = django_filters.DateTimeFilter(field_name='expires_at', lookup_expr='gte')
    expires_at_to = django_filters.DateTimeFilter(field_name='expires_at', lookup_expr='lte')
    
    # Expiration filters
    is_expired = django_filters.BooleanFilter(field_name='is_expired')
    is_valid = django_filters.BooleanFilter(field_name='is_valid')
    
    # Invited by filter
    invited_by = django_filters.ModelChoiceFilter(queryset=None)  # Will be set in view
    
    # Ordering
    ordering = django_filters.OrderingFilter(
        fields=(
            ('email', 'email'),
            ('created_at', 'created_at'),
            ('expires_at', 'expires_at'),
            ('status', 'status'),
        ),
        field_labels={
            'email': 'Email',
            'created_at': 'Created Date',
            'expires_at': 'Expires At',
            'status': 'Status',
        }
    )
    
    class Meta:
        model = Invitation
        fields = {
            'email': ['exact', 'icontains'],
        }
    
    def filter_search(self, queryset, name, value):
        """
        Search across multiple fields.
        """
        if not value:
            return queryset
        
        return queryset.filter(
            Q(email__icontains=value) |
            Q(invited_by__first_name__icontains=value) |
            Q(invited_by__last_name__icontains=value)
        )
