"""
Tenant URLs.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('', views.TenantViewSet, basename='tenants')

urlpatterns = [
    path('', include(router.urls)),
    path('current/', views.current_tenant, name='current-tenant'),
    path('current/settings/', views.update_current_tenant_settings, name='update-current-tenant-settings'),
    path('stats/', views.tenant_stats, name='tenant-stats'),
    path('admin/dashboard/', views.admin_dashboard, name='admin-dashboard'),
]
