"""
Holiday views.
"""
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from ..models import Holiday
from ..serializers import HolidaySerializer
from ..filters import HolidayFilter


class HolidayViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing holidays.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = HolidayFilter
    search_fields = ['name', 'description']
    ordering_fields = ['date', 'name']
    ordering = ['date']
    
    def get_queryset(self):
        """
        Get holidays.
        """
        return Holiday.objects.all()
    
    def get_serializer_class(self):
        """
        Return appropriate serializer.
        """
        return HolidaySerializer
