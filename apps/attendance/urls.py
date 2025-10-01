"""
Attendance URLs.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    AttendanceViewSet, LeaveTypeViewSet, LeaveBalanceViewSet,
    LeaveRequestViewSet, ShiftViewSet, HolidayViewSet
)

router = DefaultRouter()
router.register(r'attendance', AttendanceViewSet)
router.register(r'leave-types', LeaveTypeViewSet)
router.register(r'leave-balances', LeaveBalanceViewSet)
router.register(r'leave-requests', LeaveRequestViewSet)
router.register(r'shifts', ShiftViewSet)
router.register(r'holidays', HolidayViewSet)

urlpatterns = [
    path('', include(router.urls)),
]