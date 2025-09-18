"""
Employee views.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count

from .models import Employee, Department, EmployeeDocument
from .serializers import (
    EmployeeSerializer, EmployeeCreateSerializer, EmployeeUpdateSerializer,
    EmployeeListSerializer, EmployeeTerminationSerializer,
    EmployeeHierarchySerializer, DepartmentSerializer,
    DepartmentCreateSerializer, EmployeeDocumentSerializer
)


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing employees.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'status', 'employment_type', 'manager']
    search_fields = ['first_name', 'last_name', 'employee_id', 'email', 'position']
    ordering_fields = ['last_name', 'hire_date', 'department', 'position']
    ordering = ['last_name', 'first_name']
    
    def get_queryset(self):
        """
        Filter employees by tenant.
        """
        if hasattr(self.request, 'tenant_id'):
            queryset = Employee.objects.filter(tenant_id=self.request.tenant_id)
            
            # Additional filters
            status_filter = self.request.query_params.get('status')
            if status_filter == 'active':
                queryset = queryset.filter(status='active')
            elif status_filter == 'inactive':
                queryset = queryset.exclude(status='active')
            
            return queryset.select_related('manager', 'user')
        
        return Employee.objects.none()
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.
        """
        if self.action == 'list':
            return EmployeeListSerializer
        elif self.action == 'create':
            return EmployeeCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return EmployeeUpdateSerializer
        
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
        
        serializer = EmployeeTerminationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(employee)
            
            # Log the action
            from apps.audit.models import AuditLog
            AuditLog.create_log(
                request=request,
                action='employee.terminate',
                object_type='employee',
                object_id=employee.id,
                diff={'status': {'old': 'active', 'new': 'terminated'}}
            )
            
            return Response({
                'message': 'Employee terminated successfully',
                'employee': EmployeeSerializer(employee).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def reactivate(self, request, pk=None):
        """
        Reactivate a terminated employee.
        """
        employee = self.get_object()
        
        if employee.status != 'terminated':
            return Response({
                'error': 'Employee is not terminated'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        employee.reactivate()
        
        # Log the action
        from apps.audit.models import AuditLog
        AuditLog.create_log(
            request=request,
            action='employee.reactivate',
            object_type='employee',
            object_id=employee.id,
            diff={'status': {'old': 'terminated', 'new': 'active'}}
        )
        
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
        
        serializer = EmployeeListSerializer(hierarchy, many=True)
        return Response({
            'hierarchy': serializer.data,
            'direct_reports': EmployeeListSerializer(
                employee.get_direct_reports(), many=True
            ).data
        })
    
    @action(detail=False, methods=['get'])
    def org_chart(self, request):
        """
        Get organizational chart (top-level managers and their hierarchy).
        """
        # Get employees without managers (top-level)
        top_level = self.get_queryset().filter(
            manager__isnull=True,
            status='active'
        )
        
        serializer = EmployeeHierarchySerializer(top_level, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get employee statistics.
        """
        queryset = self.get_queryset()
        
        stats = {
            'total_employees': queryset.count(),
            'active_employees': queryset.filter(status='active').count(),
            'terminated_employees': queryset.filter(status='terminated').count(),
            'on_leave_employees': queryset.filter(status='on_leave').count(),
            'by_department': {},
            'by_employment_type': {},
            'new_hires_this_month': 0,
        }
        
        # Department breakdown
        dept_stats = queryset.values('department').annotate(
            count=Count('id')
        ).order_by('department')
        
        for stat in dept_stats:
            stats['by_department'][stat['department']] = stat['count']
        
        # Employment type breakdown
        type_stats = queryset.values('employment_type').annotate(
            count=Count('id')
        ).order_by('employment_type')
        
        for stat in type_stats:
            stats['by_employment_type'][stat['employment_type']] = stat['count']
        
        # New hires this month
        from datetime import date, datetime
        current_month = date.today().replace(day=1)
        stats['new_hires_this_month'] = queryset.filter(
            hire_date__gte=current_month
        ).count()
        
        return Response(stats)
    
    @action(detail=True, methods=['get', 'post'])
    def documents(self, request, pk=None):
        """
        Get or upload employee documents.
        """
        employee = self.get_object()
        
        if request.method == 'GET':
            documents = employee.documents.all()
            serializer = EmployeeDocumentSerializer(documents, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = EmployeeDocumentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(
                    employee=employee,
                    tenant_id=request.tenant_id,
                    uploaded_by=request.user
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing departments.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        """
        Filter departments by tenant.
        """
        if hasattr(self.request, 'tenant_id'):
            return Department.objects.filter(
                tenant_id=self.request.tenant_id
            ).select_related('parent', 'head')
        
        return Department.objects.none()
    
    def get_serializer_class(self):
        """
        Return appropriate serializer.
        """
        if self.action in ['create', 'update', 'partial_update']:
            return DepartmentCreateSerializer
        return DepartmentSerializer
    
    @action(detail=True, methods=['get'])
    def employees(self, request, pk=None):
        """
        Get all employees in a department.
        """
        department = self.get_object()
        employees = department.get_all_employees()
        
        serializer = EmployeeListSerializer(employees, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def hierarchy(self, request):
        """
        Get department hierarchy.
        """
        # Get top-level departments (no parent)
        top_level = self.get_queryset().filter(
            parent__isnull=True,
            is_active=True
        )
        
        def build_hierarchy(departments):
            result = []
            for dept in departments:
                dept_data = DepartmentSerializer(dept).data
                sub_depts = dept.sub_departments.filter(is_active=True)
                if sub_depts.exists():
                    dept_data['sub_departments'] = build_hierarchy(sub_depts)
                result.append(dept_data)
            return result
        
        hierarchy = build_hierarchy(top_level)
        return Response(hierarchy)
