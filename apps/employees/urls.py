"""
Employee URLs.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import EmployeeViewSet, DepartmentViewSet, EmployeeDocumentViewSet
router = DefaultRouter()
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'employee-documents', EmployeeDocumentViewSet, basename='employee-document')

urlpatterns = [
    path('', include(router.urls)),
]