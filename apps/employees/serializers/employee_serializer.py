"""
Employee serializers.
"""
from rest_framework import serializers
from django.db import transaction
from ..models import Employee
from apps.accounts.models import User


class EmployeeSerializer(serializers.ModelSerializer):
    """
    Serializer for Employee model.
    """
    full_name = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    years_of_service = serializers.ReadOnlyField()
    is_on_probation = serializers.ReadOnlyField()
    manager_name = serializers.CharField(source='manager.full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    department_code = serializers.CharField(source='department.code', read_only=True)
    direct_reports_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'first_name', 'last_name', 'middle_name',
            'full_name', 'email', 'phone', 'date_of_birth', 'gender',
            'marital_status', 'nationality', 'address', 'city', 'state',
            'postal_code', 'country', 'department', 'department_name',
            'department_code', 'position', 'employment_type', 'status',
            'is_active', 'hire_date', 'start_date', 'end_date',
            'probation_end_date', 'base_salary', 'currency',
            'pay_frequency', 'manager', 'manager_name', 'user',
            'user_email', 'emergency_contact', 'skills', 'certifications',
            'metadata', 'years_of_service', 'is_on_probation',
            'direct_reports_count', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'full_name', 'is_active', 'years_of_service',
            'is_on_probation', 'manager_name', 'user_email',
            'department_name', 'department_code', 'direct_reports_count',
            'created_at', 'updated_at'
        ]
    
    def get_direct_reports_count(self, obj):
        """Get count of direct reports."""
        return obj.get_direct_reports().count()
    
    def validate_employee_id(self, value):
        """
        Validate employee ID uniqueness.
        """
        queryset = Employee.objects.filter(employee_id=value)
        
        # Exclude current instance for updates
        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)
        
        if queryset.exists():
            raise serializers.ValidationError(
                "Employee ID must be unique within the organization."
            )
        
        return value
    
    def validate_manager(self, value):
        """
        Validate manager assignment.
        """
        if value and self.instance and value.id == self.instance.id:
            raise serializers.ValidationError(
                "Employee cannot be their own manager."
            )
        
        return value


class EmployeeCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating Employee with user account.
    """
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = Employee
        fields = [
            'employee_id', 'first_name', 'last_name', 'middle_name',
            'email', 'phone', 'date_of_birth', 'gender', 'marital_status',
            'nationality', 'address', 'city', 'state', 'postal_code',
            'country', 'department', 'position', 'employment_type',
            'hire_date', 'start_date', 'probation_end_date', 'base_salary',
            'currency', 'pay_frequency', 'manager', 'emergency_contact',
            'skills', 'certifications', 'password', 'confirm_password'
        ]
    
    def validate(self, attrs):
        """
        Validate password confirmation.
        """
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError(
                "Password and confirm password do not match."
            )
        return attrs
    
    def validate_employee_id(self, value):
        """
        Validate employee ID uniqueness.
        """
        if Employee.objects.filter(employee_id=value).exists():
            raise serializers.ValidationError(
                "Employee ID must be unique within the organization."
            )
        return value
    
    @transaction.atomic
    def create(self, validated_data):
        """
        Create employee and user account.
        """
        password = validated_data.pop('password')
        validated_data.pop('confirm_password')
        
        # Create user account
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=password,
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        
        # Create employee
        employee = Employee.objects.create(
            user=user,
            **validated_data
        )
        
        return employee
