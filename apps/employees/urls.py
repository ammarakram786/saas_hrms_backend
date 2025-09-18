"""
Employee URLs.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('employees', views.EmployeeViewSet, basename='employees')
router.register('departments', views.DepartmentViewSet, basename='departments')

urlpatterns = [
    path('', include(router.urls)),
]
