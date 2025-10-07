"""
Department views.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count

from ..models import Department
from ..serializers import DepartmentSerializer, DepartmentCreateSerializer
from ..filters import DepartmentFilter


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing departments.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DepartmentFilter
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'budget']
    ordering = ['name']
    
    def get_queryset(self):
        """
        Get departments.
        """
        return Department.objects.all().select_related('parent', 'head')
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.
        """
        if self.action == 'create':
            return DepartmentCreateSerializer
        return DepartmentSerializer
    
    @action(detail=True, methods=['get'])
    def employees(self, request, pk=None):
        """
        Get all employees in this department.
        """
        department = self.get_object()
        employees = department.get_all_employees()
        
        from ..serializers import EmployeeSerializer
        return Response({
            'employees': EmployeeSerializer(employees, many=True).data
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get department statistics.
        """
        dept_stats = Department.objects.annotate(
            employee_count=Count('head__employee_profile')
        ).values('name', 'code', 'employee_count', 'budget')
        
        return Response({
            'department_statistics': list(dept_stats)
        })
