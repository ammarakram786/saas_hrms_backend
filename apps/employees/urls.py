"""
Employee URLs.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import EmployeeViewSet, DepartmentViewSet, EmployeeDocumentViewSet
from .views.attendance_views import clock_in, clock_out

router = DefaultRouter()
router.register(r'employees', EmployeeViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'employee-documents', EmployeeDocumentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('attendance/clock-in/', clock_in, name='clock-in'),
    path('attendance/clock-out/', clock_out, name='clock-out'),
]