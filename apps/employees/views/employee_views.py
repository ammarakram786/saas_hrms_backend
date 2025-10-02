"""
Employee views.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count

from ..models import Employee
from ..serializers import EmployeeSerializer, EmployeeCreateSerializer
from ..filters import EmployeeFilter


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing employees.
    """
    permission_classes = [IsAuthenticated]
    def get_filter_backends(self):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    def get_filterset_class(self):
        if getattr(self, 'swagger_fake_view', False):
            return None
        return EmployeeFilter
    search_fields = ['first_name', 'last_name', 'employee_id', 'email', 'position']
    ordering_fields = ['last_name', 'hire_date', 'department', 'position']
    ordering = ['last_name', 'first_name']
    
    def get_queryset(self):
        """
        Get employees based on permissions with optimized queries.
        """
        queryset = Employee.objects.all()

        # Additional filters
        status_filter = self.request.query_params.get('status')
        if status_filter == 'active':
            queryset = queryset.filter(status='active')
        elif status_filter == 'inactive':
            queryset = queryset.exclude(status='active')

        # Optimize queries with select_related and prefetch_related
        return queryset.select_related(
            'manager', 'user', 'department'
        ).prefetch_related(
            'roles'  # If roles are accessed frequently
        )
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.
        """
        if self.action == 'create':
            return EmployeeCreateSerializer
        return EmployeeSerializer
    
    @action(detail=True, methods=['post'])
    def terminate(self, request, pk=None):
        """
        Terminate an employee.
        """
        employee = self.get_object()
        
        if employee.status == 'terminated':
            return Response({
                'error': 'Employee is already terminated'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        end_date = request.data.get('end_date')
        reason = request.data.get('reason')
        
        employee.terminate(end_date=end_date, reason=reason)
        
        return Response({
            'message': 'Employee terminated successfully',
            'employee': EmployeeSerializer(employee).data
        })
    
    @action(detail=True, methods=['post'])
    def reactivate(self, request, pk=None):
        """
        Reactivate a terminated employee.
        """
        employee = self.get_object()
        
        if employee.status != 'terminated':
            return Response({
                'error': 'Only terminated employees can be reactivated'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        employee.reactivate()
        
        return Response({
            'message': 'Employee reactivated successfully',
            'employee': EmployeeSerializer(employee).data
        })
    
    @action(detail=True, methods=['get'])
    def hierarchy(self, request, pk=None):
        """
        Get employee's organizational hierarchy.
        """
        employee = self.get_object()
        hierarchy = employee.get_org_hierarchy()
        
        return Response({
            'hierarchy': EmployeeSerializer(hierarchy, many=True).data
        })
    
    @action(detail=True, methods=['get'])
    def direct_reports(self, request, pk=None):
        """
        Get employee's direct reports.
        """
        employee = self.get_object()
        direct_reports = employee.get_direct_reports()
        
        return Response({
            'direct_reports': EmployeeSerializer(direct_reports, many=True).data
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get employee statistics.
        """
        total_employees = Employee.objects.count()
        active_employees = Employee.objects.filter(status='active').count()
        terminated_employees = Employee.objects.filter(status='terminated').count()
        
        # Department statistics
        dept_stats = Employee.objects.values('department').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Employment type statistics
        emp_type_stats = Employee.objects.values('employment_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return Response({
            'total_employees': total_employees,
            'active_employees': active_employees,
            'terminated_employees': terminated_employees,
            'department_statistics': list(dept_stats),
            'employment_type_statistics': list(emp_type_stats)
        })
