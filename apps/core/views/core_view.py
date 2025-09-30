"""
Core views for the HRMS application.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from apps.accounts.models import Permission


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint.
    """
    return Response({
        'status': 'healthy',
        'timestamp': request.build_absolute_uri(),
    })


@api_view(['GET'])
def list_permissions(request):
    """
    List all available permissions grouped by module.
    """
    permissions = Permission.objects.all().order_by('module', 'code')

    # Group permissions by module
    grouped_permissions = {}
    for permission in permissions:
        if permission.module not in grouped_permissions:
            grouped_permissions[permission.module] = []
        grouped_permissions[permission.module].append({
            'id': str(permission.id),
            'code': permission.code,
            'description': permission.description,
        })

    return Response(grouped_permissions)
