"""
Attendance URLs.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    AttendanceViewSet, LeaveTypeViewSet, LeaveBalanceViewSet,
    LeaveRequestViewSet, ShiftViewSet, HolidayViewSet
)
from .views.attendance_views import clock_in, clock_out

router = DefaultRouter()
router.register(r'attendance', AttendanceViewSet, basename='attendance')
router.register(r'leave-types', LeaveTypeViewSet, basename='leave-type')
router.register(r'leave-balances', LeaveBalanceViewSet, basename='leave-balance')
router.register(r'leave-requests', LeaveRequestViewSet, basename='leave-request')
router.register(r'shifts', ShiftViewSet, basename='shift')
router.register(r'holidays', HolidayViewSet, basename='holiday')

urlpatterns = [
    path('', include(router.urls)),
    path('clock-in/', clock_in, name='clock-in'),
    path('clock-out/', clock_out, name='clock-out'),
]