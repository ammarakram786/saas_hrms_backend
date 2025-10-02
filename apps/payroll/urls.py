"""
Payroll URLs.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PayrollPeriodViewSet, PayrollRecordViewSet, PayrollComponentViewSet

router = DefaultRouter()
router.register(r'periods', PayrollPeriodViewSet, basename='payroll-period')
router.register(r'records', PayrollRecordViewSet, basename='payroll-record')
router.register(r'components', PayrollComponentViewSet, basename='payroll-component')

urlpatterns = [
    path('', include(router.urls)),
]