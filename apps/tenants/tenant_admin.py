"""
Tenant-aware admin classes for tenant administrators.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Tenant, SubscriptionPlan, SubscriptionHistory
from .tenant_admin_site import tenant_admin_site


class TenantAwareModelAdmin(admin.ModelAdmin):
    """
    Base admin class that automatically filters by tenant context.
    """
    
    def get_queryset(self, request):
        """Filter queryset by tenant context."""
        qs = super().get_queryset(request)
        tenant = getattr(request, 'tenant', None)
        
        # Superusers can see all data
        if request.user.is_superuser:
            return qs
        
        if tenant and hasattr(self.model, 'tenant_id'):
            return qs.filter(tenant_id=tenant.id)
        elif tenant and hasattr(self.model, 'tenant'):
            return qs.filter(tenant=tenant)
        
        return qs
    
    def save_model(self, request, obj, form, change):
        """Automatically set tenant context when saving."""
        tenant = getattr(request, 'tenant', None)
        
        # Only set tenant context for non-superusers
        if not request.user.is_superuser and tenant:
            if hasattr(obj, 'tenant_id') and not obj.tenant_id:
                obj.tenant_id = tenant.id
            elif hasattr(obj, 'tenant') and not obj.tenant:
                obj.tenant = tenant
        
        super().save_model(request, obj, form, change)


@admin.register(Tenant, site=tenant_admin_site)
class TenantAwareTenantAdmin(TenantAwareModelAdmin):
    """
    Tenant admin for managing tenant settings (read-only for tenant admins).
    """
    list_display = [
        'name', 'plan', 'status', 'subscription_status',
        'user_count', 'employee_count', 'subscription_dates'
    ]
    
    readonly_fields = [
        'name', 'slug', 'domain', 'plan', 'status', 'subscription_plan',
        'subscription_id', 'subscription_status', 'subscription_start_date',
        'subscription_end_date', 'trial_end_date', 'max_users', 'max_employees',
        'billing_email', 'billing_address', 'tax_id', 'created_at', 'updated_at',
        'user_count', 'employee_count', 'subscription_info', 'settings_display'
    ]
    
    fieldsets = (
        ('Organization Information', {
            'fields': ('name', 'slug', 'domain', 'status')
        }),
        ('Subscription Details', {
            'fields': (
                'subscription_plan', 'plan', 'subscription_id', 'subscription_status',
                'subscription_start_date', 'subscription_end_date', 'trial_end_date',
                'subscription_info'
            ),
            'classes': ('collapse',)
        }),
        ('Limits & Usage', {
            'fields': (
                'max_users', 'max_employees', 'user_count', 'employee_count'
            ),
            'classes': ('collapse',)
        }),
        ('Billing Information', {
            'fields': ('billing_email', 'billing_address', 'tax_id'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('settings', 'settings_display'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        """Only show the current tenant."""
        tenant = getattr(request, 'tenant', None)
        if tenant:
            return Tenant.objects.filter(id=tenant.id)
        return Tenant.objects.none()
    
    def user_count(self, obj):
        """Display current user count."""
        return f"{obj.current_user_count}/{obj.max_users}"
    user_count.short_description = "Users"
    
    def employee_count(self, obj):
        """Display current employee count."""
        return f"{obj.current_employee_count}/{obj.max_employees}"
    employee_count.short_description = "Employees"
    
    def subscription_dates(self, obj):
        """Display subscription date range."""
        if obj.subscription_start_date and obj.subscription_end_date:
            return f"{obj.subscription_start_date.strftime('%Y-%m-%d')} to {obj.subscription_end_date.strftime('%Y-%m-%d')}"
        elif obj.subscription_start_date:
            return f"Started: {obj.subscription_start_date.strftime('%Y-%m-%d')}"
        return "No subscription"
    subscription_dates.short_description = "Subscription Period"
    
    def subscription_info(self, obj):
        """Display detailed subscription information."""
        if not obj.subscription_id:
            return "No active subscription"
        
        info = f"""
        <div style="padding: 10px; background: #f8f9fa; border-radius: 5px;">
            <strong>Subscription ID:</strong> {obj.subscription_id}<br>
            <strong>Status:</strong> <span style="color: {'green' if obj.subscription_status == 'active' else 'red'}">{obj.subscription_status or 'Unknown'}</span><br>
            <strong>Plan:</strong> {obj.get_plan_display()}<br>
        """
        
        if obj.subscription_start_date:
            info += f"<strong>Start Date:</strong> {obj.subscription_start_date.strftime('%Y-%m-%d %H:%M')}<br>"
        
        if obj.subscription_end_date:
            info += f"<strong>End Date:</strong> {obj.subscription_end_date.strftime('%Y-%m-%d %H:%M')}<br>"
        
        info += "</div>"
        return mark_safe(info)
    subscription_info.short_description = "Subscription Details"
    
    def settings_display(self, obj):
        """Display settings in a readable format."""
        if not obj.settings:
            return "No settings configured"
        
        settings_html = "<div style='max-height: 200px; overflow-y: auto;'>"
        settings_html += "<pre style='margin: 0; font-size: 12px;'>"
        settings_html += str(obj.settings).replace('{', '{\n  ').replace(',', ',\n  ').replace('}', '\n}')
        settings_html += "</pre></div>"
        return mark_safe(settings_html)
    settings_display.short_description = "Settings (JSON)"


# Register other models with tenant admin site
@admin.register(SubscriptionPlan, site=tenant_admin_site)
class TenantAwareSubscriptionPlanAdmin(TenantAwareModelAdmin):
    """
    Subscription plan admin (read-only for tenant admins).
    """
    list_display = [
        'name', 'price_monthly', 'price_yearly', 
        'max_users', 'max_employees', 'is_active'
    ]
    
    readonly_fields = [
        'name', 'slug', 'description', 'price_monthly', 'price_yearly',
        'max_users', 'max_employees', 'features', 'is_active', 'sort_order',
        'created_at', 'updated_at'
    ]
    
    def get_queryset(self, request):
        """Show all subscription plans."""
        return SubscriptionPlan.objects.all()


@admin.register(SubscriptionHistory, site=tenant_admin_site)
class TenantAwareSubscriptionHistoryAdmin(TenantAwareModelAdmin):
    """
    Subscription history admin (tenant-specific).
    """
    list_display = [
        'action', 'old_plan', 'new_plan', 
        'amount', 'currency', 'billing_period', 'created_at'
    ]
    
    readonly_fields = [
        'tenant', 'action', 'plan', 'old_plan', 'new_plan',
        'amount', 'currency', 'billing_period', 'notes', 'metadata',
        'created_at', 'updated_at'
    ]
    
    def get_queryset(self, request):
        """Filter by tenant context."""
        tenant = getattr(request, 'tenant', None)
        if tenant:
            return SubscriptionHistory.objects.filter(tenant=tenant)
        return SubscriptionHistory.objects.none()
