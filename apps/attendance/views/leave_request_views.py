"""
LeaveRequest views.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.attendance.models import LeaveRequest
from apps.attendance.serializers import LeaveRequestSerializer, LeaveApprovalSerializer
from apps.attendance.filters import LeaveRequestFilter


class LeaveRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing leave requests.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = LeaveRequestFilter
    search_fields = ['employee__first_name', 'employee__last_name', 'reason']
    ordering_fields = ['start_date', 'end_date', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Get leave requests.
        """
        return LeaveRequest.objects.all().select_related('employee', 'leave_type', 'approved_by')
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.
        """
        if self.action in ['approve', 'reject']:
            return LeaveApprovalSerializer
        return LeaveRequestSerializer
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Approve a leave request.
        """
        leave_request = self.get_object()
        
        if leave_request.status != 'pending':
            return Response({
                'error': 'Only pending requests can be approved'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        leave_request.approve(request.user)
        
        return Response({
            'message': 'Leave request approved successfully',
            'leave_request': LeaveRequestSerializer(leave_request).data
        })
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """
        Reject a leave request.
        """
        leave_request = self.get_object()
        
        if leave_request.status != 'pending':
            return Response({
                'error': 'Only pending requests can be rejected'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = LeaveApprovalSerializer(data=request.data)
        if serializer.is_valid():
            reason = serializer.validated_data.get('reason', '')
            leave_request.reject(request.user, reason)
            
            return Response({
                'message': 'Leave request rejected successfully',
                'leave_request': LeaveRequestSerializer(leave_request).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
