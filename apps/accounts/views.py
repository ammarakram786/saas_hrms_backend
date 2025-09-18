"""
Account views for authentication and user management.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import login, logout
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import User, Role, Permission, Invitation
from .serializers import (
    UserSerializer, LoginSerializer, RegisterSerializer,
    SuperUserCreateSerializer, RoleSerializer, RoleCreateSerializer,
    PermissionSerializer, InvitationSerializer, InvitationCreateSerializer,
    AcceptInvitationSerializer, AssignRoleSerializer
)
from .authentication import generate_tokens_for_user, refresh_access_token
from apps.tenants.views import IsSuperUser


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    User login endpoint.
    """
    serializer = LoginSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Generate tokens
        tokens = generate_tokens_for_user(user)
        
        # Update last login
        from django.utils import timezone
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        return Response({
            'user': UserSerializer(user).data,
            **tokens
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    User logout endpoint.
    """
    # In a production system, you might want to blacklist the token
    return Response({'message': 'Successfully logged out'})


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token_view(request):
    """
    Refresh access token using refresh token.
    """
    refresh_token = request.data.get('refresh_token')
    
    if not refresh_token:
        return Response({
            'error': 'Refresh token is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        tokens = refresh_access_token(refresh_token)
        return Response(tokens)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    User registration endpoint.
    """
    serializer = RegisterSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        tokens = generate_tokens_for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            **tokens
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsSuperUser])
def create_superuser_view(request):
    """
    Create superuser endpoint (platform admin).
    """
    serializer = SuperUserCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'user': UserSerializer(user).data,
            'message': 'Superuser created successfully'
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """
    Get current user profile.
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_profile_view(request):
    """
    Update current user profile.
    """
    serializer = UserSerializer(
        request.user,
        data=request.data,
        partial=True
    )
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users within a tenant.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter users by tenant.
        """
        if self.request.user.is_superuser:
            return User.objects.all()
        
        if hasattr(self.request, 'tenant_id'):
            return User.objects.filter(tenant_id=self.request.tenant_id)
        
        return User.objects.none()
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        Activate a user.
        """
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({'status': 'User activated'})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """
        Deactivate a user.
        """
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({'status': 'User deactivated'})


class RoleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing roles within a tenant.
    """
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter roles by tenant.
        """
        if hasattr(self.request, 'tenant_id'):
            return Role.objects.filter(tenant_id=self.request.tenant_id)
        
        return Role.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return RoleCreateSerializer
        return RoleSerializer
    
    def destroy(self, request, *args, **kwargs):
        """
        Prevent deletion of system roles.
        """
        role = self.get_object()
        if role.is_system:
            return Response({
                'error': 'System roles cannot be deleted'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def add_permissions(self, request, pk=None):
        """
        Add permissions to role.
        """
        role = self.get_object()
        permission_ids = request.data.get('permission_ids', [])
        
        permissions = Permission.objects.filter(id__in=permission_ids)
        role.permissions.add(*permissions)
        
        return Response({'status': 'Permissions added'})
    
    @action(detail=True, methods=['post'])
    def remove_permissions(self, request, pk=None):
        """
        Remove permissions from role.
        """
        role = self.get_object()
        permission_ids = request.data.get('permission_ids', [])
        
        permissions = Permission.objects.filter(id__in=permission_ids)
        role.permissions.remove(*permissions)
        
        return Response({'status': 'Permissions removed'})


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing permissions.
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]


class InvitationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing invitations within a tenant.
    """
    serializer_class = InvitationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter invitations by tenant.
        """
        if hasattr(self.request, 'tenant_id'):
            return Invitation.objects.filter(tenant_id=self.request.tenant_id)
        
        return Invitation.objects.none()
    
    def get_serializer_class(self):
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
                'error': 'Can only resend pending invitations'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update expiration date
        from datetime import datetime, timedelta
        invitation.expires_at = datetime.now() + timedelta(days=7)
        invitation.save()
        
        # Here you would typically send the invitation email
        
        return Response({'status': 'Invitation resent'})
    
    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """
        Revoke invitation.
        """
        invitation = self.get_object()
        invitation.revoke()
        return Response({'status': 'Invitation revoked'})


@api_view(['POST'])
@permission_classes([AllowAny])
def accept_invitation_view(request):
    """
    Accept invitation and create user account.
    """
    serializer = AcceptInvitationSerializer(data=request.data)
    
    if serializer.is_valid():
        with transaction.atomic():
            user = serializer.save()
            tokens = generate_tokens_for_user(user)
            
            return Response({
                'user': UserSerializer(user).data,
                **tokens,
                'message': 'Invitation accepted successfully'
            }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_roles_view(request):
    """
    Assign roles to a user.
    """
    serializer = AssignRoleSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'user': UserSerializer(user).data,
            'message': 'Roles assigned successfully'
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_permissions_view(request):
    """
    Get current user's effective permissions.
    """
    if not hasattr(request, 'tenant_id'):
        return Response({
            'error': 'Tenant context required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    permissions = request.user.effective_permissions
    roles = request.user.get_tenant_roles()
    
    return Response({
        'permissions': permissions,
        'roles': RoleSerializer(roles, many=True).data,
        'is_superuser': request.user.is_superuser
    })
