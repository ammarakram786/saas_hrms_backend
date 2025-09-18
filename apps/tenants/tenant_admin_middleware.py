"""
Middleware for tenant admin context.
"""
import logging
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from apps.core.utils import decode_jwt_token

logger = logging.getLogger(__name__)


class TenantAdminMiddleware(MiddlewareMixin):
    """
    Middleware to set tenant context for tenant_admin users.
    """
    
    TENANT_ADMIN_URLS = [
        '/tenant-admin/',
    ]
    
    def process_request(self, request):
        """
        Process the incoming request to set tenant context for tenant admin.
        """
        # Only process tenant admin URLs
        if not any(request.path.startswith(url) for url in self.TENANT_ADMIN_URLS):
            return None
        
        # Skip tenant validation for superusers
        if hasattr(request, 'user') and request.user.is_authenticated and request.user.is_superuser:
            request.tenant = None
            request.tenant_id = None
            return None
        
        # Get tenant_id from JWT token
        tenant_id = self._extract_tenant_id(request)
        
        if not tenant_id:
            return JsonResponse({
                'error': 'Tenant context required',
                'code': 'TENANT_REQUIRED'
            }, status=400)
        
        # Validate tenant
        tenant = self._validate_tenant(tenant_id)
        if not tenant:
            return JsonResponse({
                'error': 'Invalid or inactive tenant',
                'code': 'TENANT_INVALID'
            }, status=403)
        
        # Check if user has tenant_admin role
        if not self._has_tenant_admin_role(request.user, tenant):
            return JsonResponse({
                'error': 'Tenant admin access required',
                'code': 'TENANT_ADMIN_REQUIRED'
            }, status=403)
        
        # Set tenant context on request
        request.tenant = tenant
        request.tenant_id = tenant_id
        
        return None
    
    def _extract_tenant_id(self, request):
        """
        Extract tenant_id from JWT token in Authorization header.
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header.startswith('Bearer '):
            return None
        
        try:
            token = auth_header.split(' ')[1]
            payload = decode_jwt_token(token)
            return payload.get('tenant_id')
        except Exception as e:
            logger.warning(f"Failed to extract tenant_id from token: {e}")
            return None
    
    def _validate_tenant(self, tenant_id):
        """
        Validate tenant existence and status.
        """
        try:
            from apps.tenants.models import Tenant
            tenant = Tenant.objects.get(id=tenant_id)
            
            if tenant.status != 'active':
                logger.warning(f"Access attempt to inactive tenant: {tenant_id}")
                return None
            
            return tenant
        except Tenant.DoesNotExist:
            logger.warning(f"Access attempt to non-existent tenant: {tenant_id}")
            return None
        except Exception as e:
            logger.error(f"Error validating tenant {tenant_id}: {e}")
            return None
    
    def _has_tenant_admin_role(self, user, tenant):
        """
        Check if user has tenant_admin role for the given tenant.
        """
        if not user or not user.is_authenticated:
            return False
        
        try:
            from apps.accounts.models import Role
            tenant_admin_role = Role.objects.get(name='tenant_admin')
            return user.roles.filter(id=tenant_admin_role.id).exists()
        except Role.DoesNotExist:
            return False
        except Exception as e:
            logger.error(f"Error checking tenant admin role: {e}")
            return False
