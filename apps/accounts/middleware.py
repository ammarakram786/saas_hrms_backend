"""
Permission middleware for RBAC.
"""
import logging
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.urls import resolve

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add security headers to responses.
    """

    def process_response(self, request, response):
        """
        Add security headers to the response.
        """
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'

        # Only add CSP for non-API responses
        if not request.path.startswith('/api/'):
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' https://fonts.gstatic.com; "
                "connect-src 'self'"
            )

        return response


class PermissionMiddleware(MiddlewareMixin):
    """
    Middleware to check route-level permissions.
    
    This middleware ensures users have the required permissions to access 
    specific API endpoints.
    """
    
    # URL patterns that require specific permissions
    PERMISSION_ROUTES = {
        # Employee management
        'employees:employee-list': 'employee.view',
        'employees:employee-detail': 'employee.view',
        'employees:employee-create': 'employee.create',
        'employees:employee-update': 'employee.update',
        'employees:employee-destroy': 'employee.delete',
        'employees:employee-onboard': 'employee.onboard',
        'employees:employee-offboard': 'employee.offboard',
        
        # Attendance management
        'attendance:attendance-list': 'attendance.view',
        'attendance:attendance-detail': 'attendance.view',
        'attendance:attendance-create': 'attendance.create',
        'attendance:attendance-update': 'attendance.update',
        'attendance:attendance-destroy': 'attendance.delete',
        'attendance:shifts-manage': 'attendance.shift.manage',
        'attendance:clock-override': 'attendance.clock.override',
        'attendance:leave-request': 'leave.request',
        'attendance:leave-approve': 'leave.approve',
        
        # Payroll management
        'payroll:payroll-list': 'payroll.view',
        'payroll:payroll-detail': 'payroll.view',
        'payroll:payroll-create': 'payroll.create',
        'payroll:payroll-configure': 'payroll.configure',
        'payroll:payroll-run': 'payroll.run',
        'payroll:payslip-list': 'payslip.view_all',
        'payroll:payslip-detail': 'payslip.view_all',
        
        # Self-service (these are handled differently)
        'accounts:profile-update': 'profile.update_self',
        'accounts:leave-request-self': 'leave.request_self',
        'accounts:payslip-view-self': 'payslip.view_self',
        
        # Role and user management
        'accounts:role-list': 'role.manage',
        'accounts:role-create': 'role.manage',
        'accounts:role-update': 'role.manage',
        'accounts:role-destroy': 'role.manage',
        'accounts:user-invite': 'user.invite',
        'accounts:user-assign-roles': 'user.assign_roles',
        
        # System settings
        'core:system-settings': 'system.settings.update',
    }
    
    # Routes that are exempt from permission checking
    EXEMPT_ROUTES = [
        'accounts:login',
        'accounts:logout',
        'accounts:refresh-token',
        'accounts:register',
        'accounts:accept-invitation',
        'core:health-check',
        'core:list-permissions',
        'core:system-info',
    ]
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Check permissions for the requested view.
        """
        # Skip if user is not authenticated
        if not request.user or not request.user.is_authenticated:
            return None
        
        # Skip if user is superuser
        if request.user.is_superuser:
            return None
        
        try:
            # Resolve the URL to get the route name
            resolved = resolve(request.path_info)
            route_name = f"{resolved.namespace}:{resolved.url_name}" if resolved.namespace else resolved.url_name
            
            # Skip exempt routes
            if route_name in self.EXEMPT_ROUTES:
                return None
            
            # Check if route requires specific permission
            required_permission = self.PERMISSION_ROUTES.get(route_name)
            if not required_permission:
                # Route doesn't have specific permission requirement
                return None
            
            # Handle self-service routes differently
            if self._is_self_service_route(route_name, request, view_kwargs):
                return None
            
            # Check if user has required permission
            if not request.user.has_perm(required_permission):
                logger.warning(
                    f"Permission denied for user {request.user.email} "
                    f"on route {route_name} (required: {required_permission})"
                )
                return JsonResponse({
                    'error': 'Permission denied',
                    'required_permission': required_permission,
                    'code': 'PERMISSION_DENIED'
                }, status=403)
            
        except Exception as e:
            logger.error(f"Error checking permissions: {e}")
            # In case of error, let the request proceed
            # (better to be permissive than break the system)
        
        return None
    
    def _is_self_service_route(self, route_name, request, view_kwargs):
        """
        Check if this is a self-service route where users can only access their own data.
        """
        self_service_routes = [
            'accounts:profile-update',
            'accounts:leave-request-self',
            'accounts:payslip-view-self',
        ]
        
        if route_name not in self_service_routes:
            return False
        
        # For self-service routes, check if user is accessing their own data
        if route_name == 'accounts:profile-update':
            # User updating their own profile
            return True
        
        elif route_name == 'accounts:payslip-view-self':
            # User viewing their own payslips
            # This would typically be handled in the view itself
            return True
        
        elif route_name == 'accounts:leave-request-self':
            # User requesting their own leave
            return True
        
        return False
