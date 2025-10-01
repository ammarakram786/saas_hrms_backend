"""
LeaveType views.
"""
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from ..models import LeaveType
from ..serializers import LeaveTypeSerializer


class LeaveTypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing leave types.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'days_allowed_per_year']
    ordering = ['name']
    
    def get_queryset(self):
        """
        Get leave types.
        """
        return LeaveType.objects.all()
    
    def get_serializer_class(self):
        """
        Return appropriate serializer.
        """
        return LeaveTypeSerializer
