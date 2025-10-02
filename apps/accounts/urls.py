"""
Account URLs.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    login_view, logout_view, refresh_token_view, register_view,
    UserViewSet, user_permissions_view,
    RoleViewSet, InvitationViewSet, accept_invitation_view, assign_role_view
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'invitations', InvitationViewSet, basename='invitation')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('refresh-token/', refresh_token_view, name='refresh-token'),
    path('permissions/', user_permissions_view, name='user-permissions'),
    path('accept-invitation/', accept_invitation_view, name='accept-invitation'),
    path('assign-role/', assign_role_view, name='assign-role'),
]