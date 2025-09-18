"""
Tenant middleware for handling multi-tenant requests.
"""
import logging
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from apps.core.utils import decode_jwt_token

logger = logging.getLogger(__name__)


class TenantMiddleware(MiddlewareMixin):
    """
    Middleware to handle tenant context and isolation.
    
    This middleware:
    1. Extracts tenant_id from JWT token
    2. Validates tenant existence and status
    3. Sets tenant context for the request
    4. Ensures tenant-scoped data access
    """
    
    TENANT_EXEMPT_URLS = [
        '/admin/',
        '/admin',
        '/api/v1/auth/login/',
        '/api/v1/auth/register/',
        '/api/v1/auth/superuser/',
        '/api/v1/tenants/create/',
        '/api/v1/core/health/',
        '/static/',
        '/media/',
    ]
    
    def process_request(self, request):
        """
        Process the incoming request to extract and validate tenant context.
        """
        # Skip tenant validation for exempt URLs
        if self._is_exempt_url(request.path):
            # Set empty tenant context for exempt URLs
            request.tenant = None
            request.tenant_id = None
            logger.debug(f"Exempt URL accessed: {request.path}")
            return None
        
        # Skip tenant validation for superusers
        if hasattr(request, 'user') and request.user.is_authenticated and request.user.is_superuser:
            request.tenant = None
            request.tenant_id = None
            logger.debug(f"Superuser access: {request.path}")
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
        
        # Set tenant context on request
        request.tenant = tenant
        request.tenant_id = tenant_id
        
        return None
    
    def _is_exempt_url(self, path):
        """
        Check if the URL path is exempt from tenant validation.
        """
        return any(path.startswith(exempt_url) for exempt_url in self.TENANT_EXEMPT_URLS)
    
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
