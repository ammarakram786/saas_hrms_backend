"""
User views.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from ..models import User, Role, Permission
from ..serializers import UserSerializer, RegisterSerializer, AssignRoleSerializer
from ..filters import UserFilter


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = UserFilter

    search_fields = ['first_name', 'last_name', 'email']
    ordering_fields = ['first_name', 'last_name', 'email', 'created_at']
    ordering = ['last_name', 'first_name']

    # For router basename detection
    queryset = User.objects.all()
    
    def get_queryset(self):
        """
        Get users based on permissions.
        """

        if hasattr(self.request.user, 'is_effective_superuser') and self.request.user.is_effective_superuser():
            return User.objects.all().select_related('profile')
        else:
            # Regular users can only see themselves
            return User.objects.filter(id=self.request.user.id)
    
    def perform_create(self, serializer):
        """
        Create user and ensure they are not superuser.
        """
        user = serializer.save()
        # Ensure created user is not superuser
        user.is_superuser = False
        user.is_staff = False
        user.save()
    
    def get_serializer_class(self):
        """
        Return appropriate serializer.
        """
        if self.action == 'create':
            return RegisterSerializer
        return UserSerializer
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Get current user profile.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def assign_roles(self, request, pk=None):
        """
        Assign roles to user.
        """
        user = self.get_object()
        serializer = AssignRoleSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Roles assigned successfully',
                'user': UserSerializer(user).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Superuser creation removed - use management command instead


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_permissions_view(request):
    """
    Get user permissions.
    """
    user = request.user
    permissions = user.get_roles()
    
    return Response({
        'user_id': user.id,
        'roles': permissions,
        'effective_permissions': user.effective_permissions
    })
