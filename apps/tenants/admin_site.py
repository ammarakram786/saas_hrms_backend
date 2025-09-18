"""
Custom admin site for HRMS SaaS.
"""
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.shortcuts import render
from django.db.models import Count, Q, F
from django.utils import timezone
from datetime import timedelta
from .models import Tenant, SubscriptionPlan, SubscriptionHistory


class HRMSAdminSite(AdminSite):
    """
    Custom admin site for HRMS SaaS administration.
    """
    site_header = "HRMS SaaS Administration"
    site_title = "HRMS Admin"
    index_title = "Tenant & Subscription Management"
    
    def index(self, request, extra_context=None):
        """
        Custom admin index with tenant dashboard.
        """
        # Get tenant statistics
        total_tenants = Tenant.objects.count()
        active_tenants = Tenant.objects.filter(status='active').count()
        suspended_tenants = Tenant.objects.filter(status='suspended').count()
        pending_tenants = Tenant.objects.filter(status='pending').count()
        
        # Get subscription statistics
        active_subscriptions = Tenant.objects.filter(
            subscription_status='active'
        ).count()
        
        trial_tenants = Tenant.objects.filter(
            subscription_status='trialing'
        ).count()
        
        past_due_tenants = Tenant.objects.filter(
            subscription_status='past_due'
        ).count()
        
        # Get plan distribution
        plan_distribution = Tenant.objects.values('plan').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Get recent subscription changes
        recent_changes = SubscriptionHistory.objects.select_related(
            'tenant', 'plan'
        ).order_by('-created_at')[:5]
        
        # Get tenants approaching limits
        tenants_near_user_limit = []
        tenants_near_employee_limit = []
        
        # Check tenants approaching user limits
        for tenant in Tenant.objects.all():
            if tenant.max_users != -1:  # Not unlimited
                user_count = tenant.current_user_count
                if user_count >= tenant.max_users * 0.8:
                    tenants_near_user_limit.append({
                        'tenant': tenant,
                        'user_count': user_count,
                        'max_users': tenant.max_users,
                        'usage_percentage': (user_count / tenant.max_users) * 100
                    })
        
        # Check tenants approaching employee limits
        for tenant in Tenant.objects.all():
            if tenant.max_employees != -1:  # Not unlimited
                employee_count = tenant.current_employee_count
                if employee_count >= tenant.max_employees * 0.8:
                    tenants_near_employee_limit.append({
                        'tenant': tenant,
                        'employee_count': employee_count,
                        'max_employees': tenant.max_employees,
                        'usage_percentage': (employee_count / tenant.max_employees) * 100
                    })
        
        # Limit to 5 items each
        tenants_near_user_limit = tenants_near_user_limit[:5]
        tenants_near_employee_limit = tenants_near_employee_limit[:5]
        
        # Get expiring subscriptions (next 30 days)
        expiring_soon = Tenant.objects.filter(
            subscription_end_date__lte=timezone.now() + timedelta(days=30),
            subscription_end_date__gt=timezone.now(),
            subscription_status='active'
        ).order_by('subscription_end_date')[:5]
        
        # Get revenue data (mock - you'd integrate with actual payment processor)
        monthly_revenue = 0
        yearly_revenue = 0
        
        for tenant in Tenant.objects.filter(subscription_status='active'):
            if tenant.subscription_plan:
                if tenant.subscription_plan.price_monthly:
                    monthly_revenue += float(tenant.subscription_plan.price_monthly)
                if tenant.subscription_plan.price_yearly:
                    yearly_revenue += float(tenant.subscription_plan.price_yearly)
        
        context = {
            'total_tenants': total_tenants,
            'active_tenants': active_tenants,
            'suspended_tenants': suspended_tenants,
            'pending_tenants': pending_tenants,
            'active_subscriptions': active_subscriptions,
            'trial_tenants': trial_tenants,
            'past_due_tenants': past_due_tenants,
            'plan_distribution': plan_distribution,
            'recent_changes': recent_changes,
            'tenants_near_user_limit': tenants_near_user_limit,
            'tenants_near_employee_limit': tenants_near_employee_limit,
            'expiring_soon': expiring_soon,
            'monthly_revenue': monthly_revenue,
            'yearly_revenue': yearly_revenue,
        }
        
        # Add extra context if provided
        if extra_context:
            context.update(extra_context)
        
        return render(request, 'admin/index.html', context)


# Create custom admin site instance
admin_site = HRMSAdminSite(name='hrms_admin')
