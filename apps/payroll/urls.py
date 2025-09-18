"""
Payroll URLs.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('periods', views.PayrollPeriodViewSet, basename='payroll-periods')
router.register('records', views.PayrollRecordViewSet, basename='payroll-records')
router.register('components', views.PayrollComponentViewSet, basename='payroll-components')

urlpatterns = [
    path('', include(router.urls)),
]
