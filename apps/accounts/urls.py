"""
Account URLs.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('users', views.UserViewSet, basename='users')
router.register('roles', views.RoleViewSet, basename='roles')
router.register('permissions', views.PermissionViewSet, basename='permissions')
router.register('invitations', views.InvitationViewSet, basename='invitations')

urlpatterns = [
    # Authentication endpoints
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('refresh/', views.refresh_token_view, name='refresh-token'),
    path('register/', views.register_view, name='register'),
    path('superuser/create/', views.create_superuser_view, name='create-superuser'),
    
    # Profile endpoints
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.update_profile_view, name='profile-update'),
    
    # Invitation endpoints
    path('invitations/accept/', views.accept_invitation_view, name='accept-invitation'),

    # Role management endpoints
    path('assign-roles/', views.assign_roles_view, name='assign-roles'),
    path('permissions/me/', views.user_permissions_view, name='user-permissions'),
    
    # Router URLs
    path('', include(router.urls)),
]
