"""
Views for tenant management and subscription handling.
"""
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q, F
from django.utils import timezone
from datetime import timedelta
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, IsAuthenticated
from .models import Tenant, SubscriptionPlan, SubscriptionHistory
from .serializers import TenantSerializer


class IsSuperUser(BasePermission):
    """
    Allows access only to superusers.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


@staff_member_required
def admin_dashboard(request):
    """
    Custom admin dashboard for tenant and subscription management.
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
    ).order_by('-created_at')[:10]
    
    # Get tenants approaching limits
    tenants_near_user_limit = Tenant.objects.annotate(
        user_count=Count('users', filter=Q(users__is_active=True))
    ).filter(
        user_count__gte=F('max_users') * 0.8
    ).exclude(max_users=-1)  # Exclude unlimited plans
    
    tenants_near_employee_limit = Tenant.objects.annotate(
        employee_count=Count('employees', filter=Q(employees__end_date__isnull=True))
    ).filter(
        employee_count__gte=F('max_employees') * 0.8
    ).exclude(max_employees=-1)  # Exclude unlimited plans
    
    # Get expiring subscriptions (next 30 days)
    expiring_soon = Tenant.objects.filter(
        subscription_end_date__lte=timezone.now() + timedelta(days=30),
        subscription_end_date__gt=timezone.now(),
        subscription_status='active'
    ).order_by('subscription_end_date')
    
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
    
    return render(request, 'admin/tenant_dashboard.html', context)


class TenantViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tenants.
    """
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [IsAuthenticated, IsSuperUser]
    
    def get_queryset(self):
        """Filter tenants based on user permissions."""
        if self.request.user.is_superuser:
            return Tenant.objects.all()
        return Tenant.objects.none()
    
    @action(detail=False, methods=['get'])
    def current_tenant(self, request):
        """Get current tenant information."""
        # This would typically get tenant from JWT token
        return Response({'message': 'Current tenant endpoint'})
    
    @action(detail=False, methods=['post'])
    def update_current_tenant_settings(self, request):
        """Update current tenant settings."""
        return Response({'message': 'Update settings endpoint'})
    
    @action(detail=False, methods=['get'])
    def tenant_stats(self, request):
        """Get tenant statistics."""
        return Response({'message': 'Tenant stats endpoint'})


def current_tenant(request):
    """Get current tenant information."""
    from rest_framework.response import Response
    return Response({'message': 'Current tenant endpoint'})


def update_current_tenant_settings(request):
    """Update current tenant settings."""
    from rest_framework.response import Response
    return Response({'message': 'Update settings endpoint'})


def tenant_stats(request):
    """Get tenant statistics."""
    from rest_framework.response import Response
    return Response({'message': 'Tenant stats endpoint'})