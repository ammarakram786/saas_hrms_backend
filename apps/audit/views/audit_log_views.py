"""
AuditLog views.
"""
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from ..models import AuditLog
from ..serializers import AuditLogSerializer


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing audit logs (read-only).
    """
    permission_classes = [IsAuthenticated]
    def get_filter_backends(self):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['actor_username', 'model_name', 'description']
    ordering_fields = ['created_at', 'action', 'model_name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Get audit logs.
        """
        return AuditLog.objects.all()
    
    def get_serializer_class(self):
        """
        Return appropriate serializer.
        """
        return AuditLogSerializer
