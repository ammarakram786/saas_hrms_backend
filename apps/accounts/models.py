"""
User account models with RBAC (Role-Based Access Control).
"""
import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.db.models import JSONField
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone

from apps.core.models import BaseModel, TenantAwareModel


class UserManager(BaseUserManager):
    """
    Custom user manager.
    """
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user.
        """
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    """
    Custom User model with multi-tenant support.
    """
    tenant_id = models.UUIDField(null=True, blank=True, db_index=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    profile = JSONField(default=dict, blank=True)
    
    # RBAC fields
    roles = models.ManyToManyField('Role', through='UserRole', through_fields=('user', 'role'), blank=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        db_table = 'users'
        ordering = ['email']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['tenant_id']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def effective_permissions(self):
        """Get all permissions for this user across all roles."""
        if self.is_superuser:
            # Superusers have all permissions
            return list(Permission.objects.values_list('code', flat=True))
        
        # Get permissions from user's roles
        permission_codes = set()
        for role in self.roles.filter(is_active=True):
            permission_codes.update(
                role.permissions.values_list('code', flat=True)
            )
        
        return list(permission_codes)
    
    def has_perm(self, permission_code, obj=None):
        """
        Check if user has a specific permission.
        """
        if self.is_superuser:
            return True
        
        return permission_code in self.effective_permissions
    
    def has_perms(self, permission_codes, obj=None):
        """
        Check if user has all specified permissions.
        """
        if self.is_superuser:
            return True
        
        effective_perms = set(self.effective_permissions)
        return all(perm in effective_perms for perm in permission_codes)
    
    def has_module_perms(self, module_label):
        """
        Check if user has permissions for a specific module.
        """
        if self.is_superuser:
            return True
        
        effective_perms = self.effective_permissions
        return any(perm.startswith(f"{module_label}.") for perm in effective_perms)
    
    def get_tenant_roles(self):
        """Get user's roles within their tenant."""
        if not self.tenant_id:
            return Role.objects.none()
        return self.roles.filter(tenant_id=self.tenant_id)


class Permission(BaseModel):
    """
    Represents a permission that can be granted to roles.
    """
    code = models.CharField(max_length=100, unique=True)
    module = models.CharField(max_length=50)
    description = models.TextField()
    
    class Meta:
        db_table = 'permissions'
        ordering = ['module', 'code']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['module']),
        ]
    
    def __str__(self):
        return self.code


class Role(TenantAwareModel):
    """
    Represents a role that can be assigned to users.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_system = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    permissions = models.ManyToManyField(Permission, through='RolePermission', through_fields=('role', 'permission'), blank=True)
    
    class Meta:
        db_table = 'roles'
        ordering = ['name']
        unique_together = [('tenant_id', 'name')]
        indexes = [
            models.Index(fields=['tenant_id', 'name']),
            models.Index(fields=['is_system']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.tenant_id})"
    
    @property
    def permission_codes(self):
        """Get list of permission codes for this role."""
        return list(self.permissions.values_list('code', flat=True))
    
    def add_permission(self, permission_code):
        """Add a permission to this role."""
        try:
            permission = Permission.objects.get(code=permission_code)
            RolePermission.objects.get_or_create(
                role=self,
                permission=permission
            )
        except Permission.DoesNotExist:
            raise ValueError(f"Permission '{permission_code}' does not exist")
    
    def remove_permission(self, permission_code):
        """Remove a permission from this role."""
        try:
            permission = Permission.objects.get(code=permission_code)
            RolePermission.objects.filter(
                role=self,
                permission=permission
            ).delete()
        except Permission.DoesNotExist:
            pass  # Permission doesn't exist, nothing to remove


class RolePermission(BaseModel):
    """
    Many-to-many relationship between roles and permissions.
    """
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_permissions')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name='role_permissions')
    
    class Meta:
        db_table = 'role_permissions'
        unique_together = [('role', 'permission')]


class UserRole(BaseModel):
    """
    Many-to-many relationship between users and roles.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='user_roles')
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_user_roles'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_roles'
        unique_together = [('user', 'role')]


class Invitation(TenantAwareModel):
    """
    User invitation model for inviting users to join a tenant.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('expired', 'Expired'),
        ('revoked', 'Revoked'),
    ]
    
    email = models.EmailField()
    role_ids = ArrayField(models.UUIDField(), default=list)
    token = models.CharField(max_length=255, unique=True)
    expires_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    invited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sent_invitations'
    )
    accepted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='accepted_invitations'
    )
    accepted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'invitations'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant_id', 'email']),
            models.Index(fields=['token']),
            models.Index(fields=['status']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"Invitation for {self.email} to {self.tenant_id}"
    
    @property
    def is_expired(self):
        """Check if invitation has expired."""
        return timezone.now() > self.expires_at
    
    @property
    def is_valid(self):
        """Check if invitation is valid."""
        return self.status == 'pending' and not self.is_expired
    
    def expire(self):
        """Mark invitation as expired."""
        self.status = 'expired'
        self.save()
    
    def revoke(self):
        """Revoke the invitation."""
        self.status = 'revoked'
        self.save()
    
    def accept(self, user):
        """Accept the invitation."""
        if not self.is_valid:
            raise ValueError("Invitation is not valid")
        
        self.status = 'accepted'
        self.accepted_by = user
        self.accepted_at = timezone.now()
        self.save()
        
        # Assign roles to user
        roles = Role.objects.filter(id__in=self.role_ids, tenant_id=self.tenant_id)
        for role in roles:
            UserRole.objects.get_or_create(
                user=user,
                role=role,
                defaults={'assigned_by': self.invited_by}
            )
        
        return user
