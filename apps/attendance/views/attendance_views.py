"""
Attendance views.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from datetime import datetime, date

from ..models import AttendanceRecord, Employee
from ..serializers import AttendanceSerializer, ClockInSerializer, ClockOutSerializer
from ..filters import AttendanceFilter


class AttendanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing attendance records.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = AttendanceFilter
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    ordering_fields = ['date', 'check_in', 'hours_worked']
    ordering = ['-date']
    
    def get_queryset(self):
        """
        Get attendance records.
        """
        return AttendanceRecord.objects.all().select_related('employee')
    
    def get_serializer_class(self):
        """
        Return appropriate serializer.
        """
        return AttendanceSerializer
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get attendance statistics.
        """
        from django.db.models import Count, Avg
        
        # Get date range from query params
        date_from = request.query_params.get('date_from', date.today().replace(day=1))
        date_to = request.query_params.get('date_to', date.today())
        
        queryset = self.get_queryset().filter(
            date__range=[date_from, date_to]
        )
        
        # Calculate statistics
        total_records = queryset.count()
        present_count = queryset.filter(status='present').count()
        absent_count = queryset.filter(status='absent').count()
        late_count = queryset.filter(status='late').count()
        
        avg_hours = queryset.aggregate(
            avg_hours=Avg('hours_worked')
        )['avg_hours'] or 0
        
        return Response({
            'total_records': total_records,
            'present_count': present_count,
            'absent_count': absent_count,
            'late_count': late_count,
            'average_hours_worked': round(avg_hours, 2),
            'attendance_rate': round((present_count / total_records * 100) if total_records > 0 else 0, 2)
        })


@api_view(['POST'])
def clock_in(request):
    """
    Clock in an employee.
    """
    serializer = ClockInSerializer(data=request.data)
    if serializer.is_valid():
        employee_id = request.data.get('employee_id')
        employee = get_object_or_404(Employee, employee_id=employee_id)
        
        # Check if already clocked in today
        today = date.today()
        existing_record = AttendanceRecord.objects.filter(
            employee=employee,
            date=today
        ).first()
        
        if existing_record and existing_record.check_in:
            return Response({
                'error': 'Employee already clocked in today'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create or update attendance record
        attendance_record, created = AttendanceRecord.objects.update_or_create(
            employee=employee,
            date=today,
            defaults={
                'check_in': serializer.validated_data['check_in_time'],
                'shift': serializer.validated_data['shift'],
                'status': 'present',
                'notes': serializer.validated_data.get('notes', '')
            }
        )
        
        return Response({
            'message': 'Clocked in successfully',
            'attendance': AttendanceSerializer(attendance_record).data
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def clock_out(request):
    """
    Clock out an employee.
    """
    serializer = ClockOutSerializer(data=request.data)
    if serializer.is_valid():
        employee_id = request.data.get('employee_id')
        employee = get_object_or_404(Employee, employee_id=employee_id)
        
        # Get today's attendance record
        today = date.today()
        attendance_record = get_object_or_404(
            AttendanceRecord,
            employee=employee,
            date=today
        )
        
        if not attendance_record.check_in:
            return Response({
                'error': 'Employee must clock in before clocking out'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if attendance_record.check_out:
            return Response({
                'error': 'Employee already clocked out today'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update attendance record
        attendance_record.check_out = serializer.validated_data['check_out_time']
        if serializer.validated_data.get('notes'):
            attendance_record.notes = serializer.validated_data['notes']
        attendance_record.save()
        
        return Response({
            'message': 'Clocked out successfully',
            'attendance': AttendanceSerializer(attendance_record).data
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
