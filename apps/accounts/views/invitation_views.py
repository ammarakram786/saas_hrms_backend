"""
Invitation views.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from ..models import Invitation
from ..serializers import (
    InvitationSerializer, InvitationCreateSerializer, 
    AcceptInvitationSerializer, AssignRoleSerializer
)
from ..filters import InvitationFilter


class InvitationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing invitations.
    """
    permission_classes = [IsAuthenticated]
    def get_filter_backends(self):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    def get_filterset_class(self):
        if getattr(self, 'swagger_fake_view', False):
            return None
        return InvitationFilter

    search_fields = ['email']
    ordering_fields = ['email', 'created_at', 'expires_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Get invitations.
        """
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Invitation.objects.none()

        if hasattr(self.request.user, 'is_effective_superuser') and self.request.user.is_effective_superuser():
            return Invitation.objects.all().select_related('invited_by')
        else:
            # Regular users can only see invitations sent to their email
            return Invitation.objects.filter(
                email=self.request.user.email
            ).select_related('invited_by')
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.
        """
        if self.action == 'create':
            return InvitationCreateSerializer
        return InvitationSerializer
    
    @action(detail=True, methods=['post'])
    def resend(self, request, pk=None):
        """
        Resend invitation.
        """
        invitation = self.get_object()
        
        if invitation.status != 'pending':
            return Response({
                'error': 'Only pending invitations can be resent'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update expiration
        from datetime import datetime, timedelta
        invitation.expires_at = datetime.now() + timedelta(days=7)
        invitation.save()
        
        return Response({
            'message': 'Invitation resent successfully',
            'invitation': InvitationSerializer(invitation).data
        })


@api_view(['POST'])
@permission_classes([AllowAny])
def accept_invitation_view(request):
    """
    Accept invitation endpoint.
    """
    serializer = AcceptInvitationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        
        # Generate tokens
        from ..authentication import generate_tokens_for_user
        tokens = generate_tokens_for_user(user)
        
        return Response({
            'message': 'Invitation accepted successfully',
            'user': user.email,
            **tokens
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_role_view(request):
    """
    Assign role to user endpoint.
    """
    serializer = AssignRoleSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Role assigned successfully'
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
