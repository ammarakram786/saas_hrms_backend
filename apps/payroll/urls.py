"""
Payroll URLs.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PayrollPeriodViewSet, PayrollRecordViewSet, PayrollComponentViewSet

router = DefaultRouter()
router.register(r'periods', PayrollPeriodViewSet)
router.register(r'records', PayrollRecordViewSet)
router.register(r'components', PayrollComponentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]