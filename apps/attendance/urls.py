"""
Attendance URLs.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('attendance', views.AttendanceViewSet, basename='attendance')
router.register('leave-types', views.LeaveTypeViewSet, basename='leave-types')
router.register('leave-balances', views.LeaveBalanceViewSet, basename='leave-balances')
router.register('leave-requests', views.LeaveRequestViewSet, basename='leave-requests')
router.register('shifts', views.ShiftViewSet, basename='shifts')
router.register('holidays', views.HolidayViewSet, basename='holidays')

urlpatterns = [
    # Time tracking endpoints
    path('clock-in/', views.clock_in, name='clock-in'),
    path('clock-out/', views.clock_out, name='clock-out'),
    
    # Router URLs
    path('', include(router.urls)),
]
