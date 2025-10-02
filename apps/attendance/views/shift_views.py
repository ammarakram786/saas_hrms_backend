"""
Shift views.
"""
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from ..models import Shift
from ..serializers import ShiftSerializer
from ..filters import ShiftFilter


class ShiftViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing shifts.
    """
    permission_classes = [IsAuthenticated]
    def get_filter_backends(self):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ShiftFilter
    search_fields = ['name']
    ordering_fields = ['name', 'start_time', 'duration_hours']
    ordering = ['start_time']
    
    def get_queryset(self):
        """
        Get shifts.
        """
        return Shift.objects.all()
    
    def get_serializer_class(self):
        """
        Return appropriate serializer.
        """
        return ShiftSerializer
