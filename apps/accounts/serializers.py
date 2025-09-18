"""
Account serializers.
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from datetime import datetime, timedelta
import uuid

from .models import User, Role, Permission, Invitation, UserRole
from apps.core.utils import generate_invitation_token


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    """
    full_name = serializers.ReadOnlyField()
    effective_permissions = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'is_active', 'last_login', 'profile', 'effective_permissions',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'last_login', 'created_at', 'updated_at',
            'full_name', 'effective_permissions'
        ]


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        """
        Validate login credentials.
        """
        email = data.get('email')
        password = data.get('password')
        
        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError('Invalid email or password.')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            
            data['user'] = user
        else:
            raise serializers.ValidationError('Must include email and password.')
        
        return data


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'password', 'password_confirm'
        ]
    
    def validate(self, data):
        """
        Validate registration data.
        """
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return data
    
    def create(self, validated_data):
        """
        Create a new user.
        """
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user


class SuperUserCreateSerializer(serializers.Serializer):
    """
    Serializer for creating superuser (platform admin).
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    
    def validate_email(self, value):
        """
        Validate email uniqueness.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value
    
    def create(self, validated_data):
        """
        Create superuser.
        """
        return User.objects.create_superuser(**validated_data)


class PermissionSerializer(serializers.ModelSerializer):
    """
    Serializer for Permission model.
    """
    class Meta:
        model = Permission
        fields = ['id', 'code', 'module', 'description']


class RoleSerializer(serializers.ModelSerializer):
    """
    Serializer for Role model.
    """
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_codes = serializers.ReadOnlyField()
    user_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = [
            'id', 'name', 'description', 'is_system', 'is_active',
            'permissions', 'permission_codes', 'user_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_system']
    
    def get_user_count(self, obj):
        """Get number of users with this role."""
        return obj.user_roles.count()


class RoleCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating roles with permissions.
    """
    permission_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
        default=list
    )
    
    class Meta:
        model = Role
        fields = ['name', 'description', 'permission_ids']
    
    def create(self, validated_data):
        """
        Create role with permissions.
        """
        permission_ids = validated_data.pop('permission_ids', [])
        
        # Get tenant_id from request context
        request = self.context.get('request')
        tenant_id = getattr(request, 'tenant_id', None)
        
        if not tenant_id:
            raise serializers.ValidationError('Tenant context required.')
        
        # Create role
        role = Role.objects.create(
            tenant_id=tenant_id,
            **validated_data
        )
        
        # Add permissions
        if permission_ids:
            permissions = Permission.objects.filter(id__in=permission_ids)
            role.permissions.set(permissions)
        
        return role


class InvitationSerializer(serializers.ModelSerializer):
    """
    Serializer for Invitation model.
    """
    roles = RoleSerializer(source='role_ids', many=True, read_only=True)
    invited_by_name = serializers.CharField(source='invited_by.full_name', read_only=True)
    is_expired = serializers.ReadOnlyField()
    is_valid = serializers.ReadOnlyField()
    
    class Meta:
        model = Invitation
        fields = [
            'id', 'email', 'role_ids', 'roles', 'token', 'expires_at',
            'status', 'invited_by_name', 'is_expired', 'is_valid',
            'created_at', 'accepted_at'
        ]
        read_only_fields = [
            'id', 'token', 'expires_at', 'status', 'invited_by_name',
            'is_expired', 'is_valid', 'created_at', 'accepted_at'
        ]


class InvitationCreateSerializer(serializers.Serializer):
    """
    Serializer for creating invitations.
    """
    email = serializers.EmailField()
    role_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1
    )
    
    def validate_email(self, value):
        """
        Validate email doesn't already exist as user.
        """
        request = self.context.get('request')
        tenant_id = getattr(request, 'tenant_id', None)
        
        if User.objects.filter(email=value, tenant_id=tenant_id).exists():
            raise serializers.ValidationError(
                "User with this email already exists in this tenant."
            )
        
        return value
    
    def validate_role_ids(self, value):
        """
        Validate role IDs exist in tenant.
        """
        request = self.context.get('request')
        tenant_id = getattr(request, 'tenant_id', None)
        
        if not tenant_id:
            raise serializers.ValidationError('Tenant context required.')
        
        roles = Role.objects.filter(id__in=value, tenant_id=tenant_id)
        if len(roles) != len(value):
            raise serializers.ValidationError('Some role IDs are invalid.')
        
        return value
    
    def create(self, validated_data):
        """
        Create invitation.
        """
        request = self.context.get('request')
        tenant_id = getattr(request, 'tenant_id', None)
        
        # Generate invitation token
        token = generate_invitation_token(
            validated_data['email'],
            str(tenant_id),
            [str(role_id) for role_id in validated_data['role_ids']]
        )
        
        # Create invitation
        invitation = Invitation.objects.create(
            tenant_id=tenant_id,
            email=validated_data['email'],
            role_ids=validated_data['role_ids'],
            token=token,
            expires_at=datetime.now() + timedelta(days=7),
            invited_by=request.user
        )
        
        return invitation


class AcceptInvitationSerializer(serializers.Serializer):
    """
    Serializer for accepting invitations.
    """
    token = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, data):
        """
        Validate invitation acceptance.
        """
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        
        # Validate invitation token
        try:
            from apps.core.utils import decode_jwt_token
            payload = decode_jwt_token(data['token'])
            
            if payload.get('type') != 'invitation':
                raise serializers.ValidationError('Invalid invitation token.')
            
            # Get invitation
            invitation = Invitation.objects.get(token=data['token'])
            if not invitation.is_valid:
                raise serializers.ValidationError('Invitation is not valid.')
            
            data['invitation'] = invitation
            data['email'] = payload['email']
            
        except Exception:
            raise serializers.ValidationError('Invalid invitation token.')
        
        return data
    
    def create(self, validated_data):
        """
        Accept invitation and create user.
        """
        invitation = validated_data['invitation']
        
        # Create user
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            tenant_id=invitation.tenant_id,
            is_active=True
        )
        
        # Accept invitation (assigns roles)
        invitation.accept(user)
        
        return user


class UserRoleSerializer(serializers.ModelSerializer):
    """
    Serializer for UserRole model.
    """
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.full_name', read_only=True)
    
    class Meta:
        model = UserRole
        fields = [
            'id', 'user', 'user_email', 'user_name',
            'role', 'role_name', 'assigned_by_name', 'assigned_at'
        ]


class AssignRoleSerializer(serializers.Serializer):
    """
    Serializer for assigning roles to users.
    """
    user_id = serializers.UUIDField()
    role_ids = serializers.ListField(child=serializers.UUIDField())
    
    def validate_user_id(self, value):
        """
        Validate user exists in tenant.
        """
        request = self.context.get('request')
        tenant_id = getattr(request, 'tenant_id', None)
        
        try:
            user = User.objects.get(id=value, tenant_id=tenant_id)
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError('User not found in this tenant.')
    
    def validate_role_ids(self, value):
        """
        Validate roles exist in tenant.
        """
        request = self.context.get('request')
        tenant_id = getattr(request, 'tenant_id', None)
        
        roles = Role.objects.filter(id__in=value, tenant_id=tenant_id)
        if len(roles) != len(value):
            raise serializers.ValidationError('Some roles are invalid.')
        
        return value
    
    def save(self):
        """
        Assign roles to user.
        """
        request = self.context.get('request')
        user = User.objects.get(id=self.validated_data['user_id'])
        roles = Role.objects.filter(id__in=self.validated_data['role_ids'])
        
        # Clear existing roles and assign new ones
        user.roles.clear()
        for role in roles:
            UserRole.objects.create(
                user=user,
                role=role,
                assigned_by=request.user
            )
        
        return user
