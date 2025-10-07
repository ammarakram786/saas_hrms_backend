"""
URL configuration for HRMS project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions

urlpatterns = [
    path('admin/', admin.site.urls),  # Django admin site
    path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/employees/', include('apps.employees.urls')),
    path('api/v1/attendance/', include('apps.attendance.urls')),
    path('api/v1/payroll/', include('apps.payroll.urls')),
    path('api/v1/audit/', include('apps.audit.urls')),
    path('api/v1/core/', include('apps.core.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
