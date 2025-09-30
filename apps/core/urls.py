"""
Core app URLs.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.core import views

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('health/', views.health_check, name='health-check'),
    path('permissions/', views.list_permissions, name='list-permissions'),
]
