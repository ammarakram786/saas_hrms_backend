"""
Tenant-aware admin site for tenant administrators.
"""
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.shortcuts import render
from django.db.models import Count, Q, F
from django.utils import timezone
from datetime import timedelta
from .models import Tenant, SubscriptionPlan, SubscriptionHistory


class TenantAdminSite(AdminSite):
    """
    Tenant-aware admin site that filters data by tenant context.
    """
    site_header = "Tenant Administration"
    site_title = "Tenant Admin"
    index_title = "Manage Your Organization"
    
    def index(self, request, extra_context=None):
        """
        Custom admin index with tenant-specific dashboard.
        """
        # Get tenant from request (set by middleware)
        tenant = getattr(request, 'tenant', None)
        
        # For superusers, redirect to main admin
        if request.user.is_superuser:
            from django.shortcuts import redirect
            return redirect('/admin/')
        
        if not tenant:
            return render(request, 'admin/tenant_required.html', {
                'error': 'Tenant context required. Please contact system administrator.'
            })
        
        # Get tenant-specific statistics
        total_users = 0
        total_employees = 0
        active_users = 0
        active_employees = 0
        
        try:
            from apps.accounts.models import User
            total_users = User.objects.filter(tenant_id=tenant.id).count()
            active_users = User.objects.filter(tenant_id=tenant.id, is_active=True).count()
        except ImportError:
            pass
        
        try:
            from apps.employees.models import Employee
            total_employees = Employee.objects.filter(tenant_id=tenant.id).count()
            active_employees = Employee.objects.filter(tenant_id=tenant.id, end_date__isnull=True).count()
        except ImportError:
            pass
        
        # Get recent activity within tenant
        recent_changes = SubscriptionHistory.objects.filter(
            tenant=tenant
        ).order_by('-created_at')[:5]
        
        # Check if approaching limits
        user_limit_warning = False
        employee_limit_warning = False
        
        if tenant.max_users != -1 and active_users >= tenant.max_users * 0.8:
            user_limit_warning = True
        
        if tenant.max_employees != -1 and active_employees >= tenant.max_employees * 0.8:
            employee_limit_warning = True
        
        # Get subscription info
        subscription_info = {
            'plan': tenant.get_plan_display(),
            'status': tenant.subscription_status or 'No subscription',
            'start_date': tenant.subscription_start_date,
            'end_date': tenant.subscription_end_date,
            'max_users': tenant.max_users,
            'max_employees': tenant.max_employees,
        }
        
        context = {
            'tenant': tenant,
            'total_users': total_users,
            'active_users': active_users,
            'total_employees': total_employees,
            'active_employees': active_employees,
            'recent_changes': recent_changes,
            'user_limit_warning': user_limit_warning,
            'employee_limit_warning': employee_limit_warning,
            'subscription_info': subscription_info,
        }
        
        # Add extra context if provided
        if extra_context:
            context.update(extra_context)
        
        return render(request, 'admin/tenant_index.html', context)


# Create tenant admin site instance
tenant_admin_site = TenantAdminSite(name='tenant_admin')
