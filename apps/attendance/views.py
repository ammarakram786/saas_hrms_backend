"""
Attendance views.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Count
from django.shortcuts import get_object_or_404
from datetime import date, datetime, timedelta

from .models import (
    AttendanceRecord, LeaveType, LeaveBalance,
    LeaveRequest, Shift, Holiday
)
from .serializers import (
    AttendanceRecordSerializer, ClockInSerializer, ClockOutSerializer,
    LeaveTypeSerializer, LeaveBalanceSerializer, LeaveRequestSerializer,
    LeaveRequestActionSerializer, ShiftSerializer, HolidaySerializer
)
from apps.employees.models import Employee


class AttendanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing attendance records.
    """
    serializer_class = AttendanceRecordSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'status', 'shift', 'leave_type']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    ordering_fields = ['date', 'check_in', 'check_out', 'hours_worked']
    ordering = ['-date']
    
    def get_queryset(self):
        """
        Filter attendance by tenant and date range.
        """
        if hasattr(self.request, 'tenant_id'):
            queryset = AttendanceRecord.objects.filter(
                tenant_id=self.request.tenant_id
            ).select_related('employee')
            
            # Date range filtering
            start_date = self.request.query_params.get('start_date')
            end_date = self.request.query_params.get('end_date')
            
            if start_date:
                queryset = queryset.filter(date__gte=start_date)
            if end_date:
                queryset = queryset.filter(date__lte=end_date)
            
            return queryset
        
        return AttendanceRecord.objects.none()
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """
        Get today's attendance for all employees.
        """
        today = date.today()
        attendance = self.get_queryset().filter(date=today)
        serializer = self.get_serializer(attendance, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get attendance summary for a date range.
        """
        start_date = request.query_params.get('start_date', str(date.today() - timedelta(days=30)))
        end_date = request.query_params.get('end_date', str(date.today()))
        
        queryset = self.get_queryset().filter(
            date__gte=start_date,
            date__lte=end_date
        )
        
        summary = {
            'total_records': queryset.count(),
            'present': queryset.filter(status='present').count(),
            'absent': queryset.filter(status='absent').count(),
            'late': queryset.filter(status='late').count(),
            'on_leave': queryset.filter(status='on_leave').count(),
            'total_hours': queryset.aggregate(
                total=Sum('hours_worked')
            )['total'] or 0,
            'overtime_hours': queryset.aggregate(
                total=Sum('overtime_hours')
            )['total'] or 0,
        }
        
        return Response(summary)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clock_in(request):
    """
    Clock in for the current user.
    """
    # Get employee record for user
    try:
        employee = Employee.objects.get(
            tenant_id=request.tenant_id,
            user=request.user
        )
    except Employee.DoesNotExist:
        return Response({
            'error': 'Employee record not found'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = ClockInSerializer(data=request.data)
    if serializer.is_valid():
        today = date.today()
        check_in_time = serializer.validated_data['check_in_time']
        
        # Check if already clocked in today
        existing = AttendanceRecord.objects.filter(
            tenant_id=request.tenant_id,
            employee=employee,
            date=today
        ).first()
        
        if existing and existing.check_in:
            return Response({
                'error': 'Already clocked in today'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create or update attendance record
        attendance, created = AttendanceRecord.objects.update_or_create(
            tenant_id=request.tenant_id,
            employee=employee,
            date=today,
            defaults={
                'check_in': check_in_time,
                'status': 'present',
                'shift': serializer.validated_data.get('shift', 'regular'),
                'notes': serializer.validated_data.get('notes', ''),
            }
        )
        
        return Response({
            'message': 'Clocked in successfully',
            'attendance': AttendanceRecordSerializer(attendance).data
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clock_out(request):
    """
    Clock out for the current user.
    """
    # Get employee record for user
    try:
        employee = Employee.objects.get(
            tenant_id=request.tenant_id,
            user=request.user
        )
    except Employee.DoesNotExist:
        return Response({
            'error': 'Employee record not found'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = ClockOutSerializer(data=request.data)
    if serializer.is_valid():
        today = date.today()
        check_out_time = serializer.validated_data['check_out_time']
        
        # Get today's attendance record
        try:
            attendance = AttendanceRecord.objects.get(
                tenant_id=request.tenant_id,
                employee=employee,
                date=today
            )
        except AttendanceRecord.DoesNotExist:
            return Response({
                'error': 'No clock-in record found for today'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if attendance.check_out:
            return Response({
                'error': 'Already clocked out today'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update attendance record
        attendance.check_out = check_out_time
        attendance.notes = serializer.validated_data.get('notes', attendance.notes)
        attendance.save()  # This will calculate hours_worked
        
        return Response({
            'message': 'Clocked out successfully',
            'attendance': AttendanceRecordSerializer(attendance).data
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LeaveTypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing leave types.
    """
    serializer_class = LeaveTypeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code']
    ordering = ['name']
    
    def get_queryset(self):
        """
        Filter leave types by tenant.
        """
        if hasattr(self.request, 'tenant_id'):
            return LeaveType.objects.filter(tenant_id=self.request.tenant_id)
        return LeaveType.objects.none()
    
    def perform_create(self, serializer):
        """
        Create leave type with tenant context.
        """
        serializer.save(tenant_id=self.request.tenant_id)


class LeaveBalanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing leave balances.
    """
    serializer_class = LeaveBalanceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['employee', 'leave_type', 'year']
    ordering_fields = ['year', 'allocated_days', 'used_days']
    ordering = ['-year', 'leave_type__name']
    
    def get_queryset(self):
        """
        Filter leave balances by tenant.
        """
        if hasattr(self.request, 'tenant_id'):
            return LeaveBalance.objects.filter(
                tenant_id=self.request.tenant_id
            ).select_related('employee', 'leave_type')
        return LeaveBalance.objects.none()
    
    def perform_create(self, serializer):
        """
        Create leave balance with tenant context.
        """
        serializer.save(tenant_id=self.request.tenant_id)


class LeaveRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing leave requests.
    """
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'leave_type', 'status']
    search_fields = ['employee__first_name', 'employee__last_name', 'reason']
    ordering_fields = ['created_at', 'start_date', 'end_date']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Filter leave requests by tenant and user permissions.
        """
        if hasattr(self.request, 'tenant_id'):
            queryset = LeaveRequest.objects.filter(
                tenant_id=self.request.tenant_id
            ).select_related('employee', 'leave_type', 'approved_by')
            
            # If user doesn't have leave.view permission, only show their own requests
            if not self.request.user.has_perm('leave.approve'):
                try:
                    employee = Employee.objects.get(
                        tenant_id=self.request.tenant_id,
                        user=self.request.user
                    )
                    queryset = queryset.filter(employee=employee)
                except Employee.DoesNotExist:
                    return LeaveRequest.objects.none()
            
            return queryset
        
        return LeaveRequest.objects.none()
    
    @action(detail=True, methods=['post'])
    def approve_reject(self, request, pk=None):
        """
        Approve or reject leave request.
        """
        leave_request = self.get_object()
        
        if leave_request.status != 'pending':
            return Response({
                'error': 'Can only approve/reject pending requests'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = LeaveRequestActionSerializer(data=request.data)
        if serializer.is_valid():
            action = serializer.validated_data['action']
            reason = serializer.validated_data.get('reason', '')
            
            try:
                if action == 'approve':
                    leave_request.approve(request.user)
                    message = 'Leave request approved'
                else:
                    leave_request.reject(request.user, reason)
                    message = 'Leave request rejected'
                
                return Response({
                    'message': message,
                    'leave_request': LeaveRequestSerializer(leave_request).data
                })
                
            except Exception as e:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ShiftViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing shifts.
    """
    serializer_class = ShiftSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter shifts by tenant.
        """
        if hasattr(self.request, 'tenant_id'):
            return Shift.objects.filter(tenant_id=self.request.tenant_id)
        return Shift.objects.none()
    
    def perform_create(self, serializer):
        """
        Create shift with tenant context.
        """
        serializer.save(tenant_id=self.request.tenant_id)


class HolidayViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing holidays.
    """
    serializer_class = HolidaySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_optional']
    ordering_fields = ['date', 'name']
    ordering = ['date']
    
    def get_queryset(self):
        """
        Filter holidays by tenant and year.
        """
        if hasattr(self.request, 'tenant_id'):
            queryset = Holiday.objects.filter(tenant_id=self.request.tenant_id)
            
            # Filter by year if provided
            year = self.request.query_params.get('year')
            if year:
                queryset = queryset.filter(date__year=year)
            
            return queryset
        
        return Holiday.objects.none()
    
    def perform_create(self, serializer):
        """
        Create holiday with tenant context.
        """
        serializer.save(tenant_id=self.request.tenant_id)
