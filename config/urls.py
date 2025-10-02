"""
URL configuration for HRMS project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg import openapi


class CustomOpenAPISchemaGenerator(OpenAPISchemaGenerator):
    def get_operation(self, view, path, prefix, method, components, request):
        """Override to handle duplicate parameters"""
        try:
            return super().get_operation(view, path, prefix, method, components, request)
        except AssertionError as e:
            if "duplicate Parameters found" in str(e):
                # Handle duplicate parameters by creating a simple operation
                from drf_yasg.openapi import Operation, Response
                responses = {
                    '200': Response(description='Success')
                }
                operation = Operation(
                    operation_id=f"{view.__class__.__name__}_{method.lower()}",
                    summary=f"{view.__class__.__name__} {method.upper()}",
                    responses=responses
                )
                return operation
            raise

# API Documentation Schema View
schema_view = get_schema_view(
    openapi.Info(
        title="HRMS API",
        default_version='v1',
        description="Human Resource Management System API Documentation",
        terms_of_service="https://www.example.com/policies/terms/",
        contact=openapi.Contact(email="admin@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    generator_class=CustomOpenAPISchemaGenerator,
    url='http://localhost:8000',  # Replace with your actual API base URL
)

urlpatterns = [
    path('admin/', admin.site.urls),  # Django admin site
    path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/employees/', include('apps.employees.urls')),
    path('api/v1/attendance/', include('apps.attendance.urls')),
    path('api/v1/payroll/', include('apps.payroll.urls')),
    path('api/v1/audit/', include('apps.audit.urls')),
    path('api/v1/core/', include('apps.core.urls')),

    # API Documentation
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
