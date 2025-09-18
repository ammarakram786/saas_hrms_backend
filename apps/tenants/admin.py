"""
Admin interface for Tenant management.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Q
from django.utils import timezone
from .models import Tenant, SubscriptionPlan, SubscriptionHistory


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    """
    Admin interface for Tenant management with subscription support.
    """
    list_display = [
        'name', 'slug', 'plan', 'status', 'subscription_status',
        'user_count', 'employee_count', 'subscription_dates',
        'contact_email', 'created_at', 'is_active'
    ]
    
    list_filter = [
        'plan', 'status', 'subscription_status', 'created_at',
        'subscription_start_date', 'subscription_end_date'
    ]
    
    search_fields = [
        'name', 'slug', 'contact_email', 'subscription_id',
        'contact_phone', 'address'
    ]
    
    readonly_fields = [
        'slug', 'created_at', 'updated_at', 'user_count',
        'employee_count', 'subscription_info', 'settings_display'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'domain', 'status', 'created_by')
        }),
        ('Subscription Details', {
            'fields': (
                'subscription_plan', 'plan', 'subscription_id', 'subscription_status',
                'subscription_start_date', 'subscription_end_date', 'trial_end_date',
                'subscription_info'
            ),
            'classes': ('collapse',)
        }),
        ('Billing Information', {
            'fields': ('billing_email', 'billing_address', 'tax_id'),
            'classes': ('collapse',)
        }),
        ('Limits & Usage', {
            'fields': (
                'max_users', 'max_employees', 'user_count', 'employee_count'
            ),
            'classes': ('collapse',)
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone', 'address'),
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
    
    actions = [
        'activate_tenants', 'suspend_tenants', 'upgrade_to_premium',
        'downgrade_to_basic', 'extend_subscription', 'reset_limits'
    ]
    
    def get_queryset(self, request):
        """Optimize queryset with related data."""
        return super().get_queryset(request).select_related()
    
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
    
    def is_active(self, obj):
        """Display active status with color coding."""
        if obj.status == 'active':
            return format_html('<span style="color: green;">✓ Active</span>')
        elif obj.status == 'suspended':
            return format_html('<span style="color: red;">⚠ Suspended</span>')
        elif obj.status == 'pending':
            return format_html('<span style="color: orange;">⏳ Pending</span>')
        else:
            return format_html('<span style="color: gray;">✗ Inactive</span>')
    is_active.short_description = "Status"
    is_active.admin_order_field = 'status'
    
    # Admin Actions
    def activate_tenants(self, request, queryset):
        """Activate selected tenants."""
        updated = queryset.update(status='active')
        self.message_user(request, f"Successfully activated {updated} tenants.")
    activate_tenants.short_description = "Activate selected tenants"
    
    def suspend_tenants(self, request, queryset):
        """Suspend selected tenants."""
        updated = queryset.update(status='suspended')
        self.message_user(request, f"Successfully suspended {updated} tenants.")
    suspend_tenants.short_description = "Suspend selected tenants"
    
    def upgrade_to_premium(self, request, queryset):
        """Upgrade selected tenants to premium plan."""
        updated = queryset.update(plan='premium')
        self.message_user(request, f"Successfully upgraded {updated} tenants to premium.")
    upgrade_to_premium.short_description = "Upgrade to Premium plan"
    
    def downgrade_to_basic(self, request, queryset):
        """Downgrade selected tenants to basic plan."""
        updated = queryset.update(plan='basic')
        self.message_user(request, f"Successfully downgraded {updated} tenants to basic.")
    downgrade_to_basic.short_description = "Downgrade to Basic plan"
    
    def extend_subscription(self, request, queryset):
        """Extend subscription by 30 days."""
        from datetime import datetime, timedelta
        
        extended_count = 0
        for tenant in queryset:
            if tenant.subscription_end_date:
                tenant.subscription_end_date += timedelta(days=30)
            else:
                tenant.subscription_end_date = datetime.now() + timedelta(days=30)
            tenant.save()
            extended_count += 1
        
        self.message_user(request, f"Successfully extended subscription for {extended_count} tenants.")
    extend_subscription.short_description = "Extend subscription by 30 days"
    
    def reset_limits(self, request, queryset):
        """Reset usage limits for selected tenants."""
        updated = queryset.update(
            max_users=50,
            max_employees=200
        )
        self.message_user(request, f"Successfully reset limits for {updated} tenants.")
    reset_limits.short_description = "Reset usage limits"
    
    def save_model(self, request, obj, form, change):
        """Custom save logic."""
        if not change:  # Creating new tenant
            obj.created_by = request.user.id if request.user.is_authenticated else None
            obj.initialize_settings()
        super().save_model(request, obj, form, change)


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    """
    Admin interface for Subscription Plan management.
    """
    list_display = [
        'name', 'slug', 'price_monthly', 'price_yearly', 
        'max_users', 'max_employees', 'is_active', 'sort_order'
    ]
    
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'slug', 'description']
    ordering = ['sort_order', 'name']
    
    fieldsets = (
        ('Plan Information', {
            'fields': ('name', 'slug', 'description', 'is_active', 'sort_order')
        }),
        ('Pricing', {
            'fields': ('price_monthly', 'price_yearly')
        }),
        ('Limits', {
            'fields': ('max_users', 'max_employees')
        }),
        ('Features', {
            'fields': ('features',),
            'classes': ('collapse',)
        })
    )


@admin.register(SubscriptionHistory)
class SubscriptionHistoryAdmin(admin.ModelAdmin):
    """
    Admin interface for Subscription History.
    """
    list_display = [
        'tenant', 'action', 'old_plan', 'new_plan', 
        'amount', 'currency', 'billing_period', 'created_at'
    ]
    
    list_filter = [
        'action', 'currency', 'billing_period', 'created_at'
    ]
    
    search_fields = [
        'tenant__name', 'action', 'old_plan', 'new_plan', 'notes'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Subscription Change', {
            'fields': ('tenant', 'action', 'plan', 'old_plan', 'new_plan')
        }),
        ('Billing Details', {
            'fields': ('amount', 'currency', 'billing_period')
        }),
        ('Additional Information', {
            'fields': ('notes', 'metadata'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        """Optimize queryset with related data."""
        return super().get_queryset(request).select_related('tenant', 'plan')


# Import custom admin site
from .admin_site import admin_site

# Register models with custom admin site
admin_site.register(Tenant, TenantAdmin)
admin_site.register(SubscriptionPlan, SubscriptionPlanAdmin)
admin_site.register(SubscriptionHistory, SubscriptionHistoryAdmin)

# Also register with default admin site for fallback
admin.site.site_header = "HRMS SaaS Administration"
admin.site.site_title = "HRMS Admin"
admin.site.index_title = "Tenant & Subscription Management"
