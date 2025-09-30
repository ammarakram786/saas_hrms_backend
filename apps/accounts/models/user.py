"""
User account models with RBAC (Role-Based Access Control).
"""
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.db.models import JSONField

from .permission import Permission
from apps.core.models import BaseModel
from .role import Role


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





