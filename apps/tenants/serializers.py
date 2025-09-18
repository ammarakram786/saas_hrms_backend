"""
Tenant serializers.
"""
from rest_framework import serializers
from .models import Tenant


class TenantSerializer(serializers.ModelSerializer):
    """
    Serializer for Tenant model.
    """
    current_user_count = serializers.ReadOnlyField()
    current_employee_count = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    
    class Meta:
        model = Tenant
        fields = [
            'id', 'name', 'slug', 'domain', 'plan', 'status',
            'contact_email', 'contact_phone', 'address',
            'max_users', 'max_employees', 'current_user_count',
            'current_employee_count', 'is_active', 'settings',
            'subscription_status', 'subscription_start_date',
            'subscription_end_date', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'current_user_count',
            'current_employee_count', 'is_active'
        ]


class TenantCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new tenant.
    """
    admin_email = serializers.EmailField(write_only=True)
    admin_password = serializers.CharField(write_only=True, min_length=8)
    admin_first_name = serializers.CharField(write_only=True)
    admin_last_name = serializers.CharField(write_only=True)
    
    class Meta:
        model = Tenant
        fields = [
            'name', 'slug', 'domain', 'plan', 'contact_email',
            'contact_phone', 'address', 'max_users', 'max_employees',
            'admin_email', 'admin_password', 'admin_first_name', 'admin_last_name'
        ]
    
    def validate_slug(self, value):
        """
        Validate that slug is unique.
        """
        if Tenant.objects.filter(slug=value).exists():
            raise serializers.ValidationError("A tenant with this slug already exists.")
        return value
    
    def create(self, validated_data):
        """
        Create tenant and admin user.
        """
        # Extract admin user data
        admin_data = {
            'email': validated_data.pop('admin_email'),
            'password': validated_data.pop('admin_password'),
            'first_name': validated_data.pop('admin_first_name'),
            'last_name': validated_data.pop('admin_last_name'),
        }
        
        # Create tenant
        tenant = Tenant.objects.create(**validated_data, status='active')
        tenant.initialize_settings()
        
        # Create admin user
        from apps.accounts.models import User, Role
        admin_user = User.objects.create_user(
            email=admin_data['email'],
            password=admin_data['password'],
            first_name=admin_data['first_name'],
            last_name=admin_data['last_name'],
            tenant_id=tenant.id,
            is_active=True
        )
        
        # Assign tenant admin role
        admin_role = Role.objects.create(
            tenant_id=tenant.id,
            name='Tenant Admin',
            description='Full access to tenant resources',
            is_system=True
        )
        
        # Assign all permissions to admin role
        from apps.accounts.models import Permission
        permissions = Permission.objects.all()
        admin_role.permissions.set(permissions)
        
        # Assign role to admin user
        admin_user.roles.add(admin_role)
        
        return tenant


class TenantSettingsSerializer(serializers.Serializer):
    """
    Serializer for updating tenant settings.
    """
    timezone = serializers.CharField(required=False)
    date_format = serializers.CharField(required=False)
    currency = serializers.CharField(required=False)
    working_hours = serializers.DictField(required=False)
    leave_policy = serializers.DictField(required=False)
    payroll_settings = serializers.DictField(required=False)
    notification_settings = serializers.DictField(required=False)
    features = serializers.DictField(required=False)
    
    def update(self, instance, validated_data):
        """
        Update tenant settings.
        """
        for key, value in validated_data.items():
            instance.update_setting(key, value)
        return instance
