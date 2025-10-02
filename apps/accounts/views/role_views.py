"""
Role views.
"""
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from ..models import Role
from ..serializers import RoleSerializer, RoleCreateSerializer
from ..filters import RoleFilter


class RoleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing roles.
    """
    permission_classes = [IsAuthenticated]
    def get_filter_backends(self):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = RoleFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        """
        Get roles.
        """
        return Role.objects.all().prefetch_related('permissions')
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.
        """
        if self.action == 'create':
            return RoleCreateSerializer
        return RoleSerializer
