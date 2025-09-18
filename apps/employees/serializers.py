"""
Employee serializers.
"""
from rest_framework import serializers
from django.db import transaction

from .models import Employee, EmployeeDocument, Department
from apps.accounts.models import User


class DepartmentSerializer(serializers.ModelSerializer):
    """
    Serializer for Department model.
    """
    employee_count = serializers.ReadOnlyField()
    head_name = serializers.CharField(source='head.full_name', read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    
    class Meta:
        model = Department
        fields = [
            'id', 'name', 'code', 'description', 'parent', 'parent_name',
            'head', 'head_name', 'budget', 'cost_center', 'is_active',
            'employee_count', 'created_at', 'updated_at'
        ]


class EmployeeDocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for EmployeeDocument model.
    """
    uploaded_by_name = serializers.CharField(source='uploaded_by.full_name', read_only=True)
    
    class Meta:
        model = EmployeeDocument
        fields = [
            'id', 'name', 'document_type', 'file_path', 'file_size',
            'mime_type', 'is_confidential', 'uploaded_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uploaded_by_name', 'created_at', 'updated_at']


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
    direct_reports_count = serializers.SerializerMethodField()
    documents = EmployeeDocumentSerializer(source='employee_documents', many=True, read_only=True)
    
    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'first_name', 'last_name', 'middle_name',
            'full_name', 'email', 'phone', 'date_of_birth', 'gender',
            'marital_status', 'nationality', 'address', 'city', 'state',
            'postal_code', 'country', 'department', 'position',
            'employment_type', 'status', 'is_active', 'hire_date',
            'start_date', 'end_date', 'probation_end_date',
            'base_salary', 'currency', 'pay_frequency', 'manager',
            'manager_name', 'user', 'user_email', 'emergency_contact',
            'skills', 'certifications', 'metadata', 'years_of_service',
            'is_on_probation', 'direct_reports_count', 'documents',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'full_name', 'is_active', 'years_of_service',
            'is_on_probation', 'manager_name', 'user_email',
            'direct_reports_count', 'created_at', 'updated_at'
        ]
    
    def get_direct_reports_count(self, obj):
        """Get count of direct reports."""
        return obj.get_direct_reports().count()
    
    def validate_employee_id(self, value):
        """
        Validate employee ID uniqueness within tenant.
        """
        request = self.context.get('request')
        tenant_id = getattr(request, 'tenant_id', None)
        
        if tenant_id:
            queryset = Employee.objects.filter(
                tenant_id=tenant_id,
                employee_id=value
            )
            
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
        Validate manager assignment (prevent circular references).
        """
        if value and self.instance:
            # Check for circular reference
            current = value
            while current:
                if current == self.instance:
                    raise serializers.ValidationError(
                        "Cannot assign employee as their own manager (circular reference)."
                    )
                current = current.manager
        
        return value
    
    def create(self, validated_data):
        """
        Create employee with tenant context.
        """
        request = self.context.get('request')
        tenant_id = getattr(request, 'tenant_id', None)
        
        if tenant_id:
            validated_data['tenant_id'] = tenant_id
        
        return super().create(validated_data)


class EmployeeCreateSerializer(EmployeeSerializer):
    """
    Serializer for creating employees with user account.
    """
    create_user_account = serializers.BooleanField(default=False, write_only=True)
    user_password = serializers.CharField(write_only=True, required=False)
    user_roles = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
        default=list
    )
    
    class Meta(EmployeeSerializer.Meta):
        fields = EmployeeSerializer.Meta.fields + [
            'create_user_account', 'user_password', 'user_roles'
        ]
    
    def validate(self, data):
        """
        Validate employee creation data.
        """
        if data.get('create_user_account'):
            if not data.get('user_password'):
                raise serializers.ValidationError(
                    "Password is required when creating user account."
                )
        
        return data
    
    @transaction.atomic
    def create(self, validated_data):
        """
        Create employee and optionally create user account.
        """
        request = self.context.get('request')
        tenant_id = getattr(request, 'tenant_id', None)
        
        # Extract user-related data
        create_user_account = validated_data.pop('create_user_account', False)
        user_password = validated_data.pop('user_password', None)
        user_roles = validated_data.pop('user_roles', [])
        
        # Set tenant context
        if tenant_id:
            validated_data['tenant_id'] = tenant_id
        
        # Create employee
        employee = Employee.objects.create(**validated_data)
        
        # Create user account if requested
        if create_user_account and user_password:
            user = User.objects.create_user(
                email=employee.email,
                password=user_password,
                first_name=employee.first_name,
                last_name=employee.last_name,
                tenant_id=tenant_id,
                is_active=True
            )
            
            # Link user to employee
            employee.user = user
            employee.save()
            
            # Assign roles if provided
            if user_roles:
                from apps.accounts.models import Role, UserRole
                roles = Role.objects.filter(
                    id__in=user_roles,
                    tenant_id=tenant_id
                )
                
                for role in roles:
                    UserRole.objects.create(
                        user=user,
                        role=role,
                        assigned_by=request.user
                    )
        
        return employee


class EmployeeUpdateSerializer(EmployeeSerializer):
    """
    Serializer for updating employees.
    """
    class Meta(EmployeeSerializer.Meta):
        # Don't allow changing employee_id after creation
        read_only_fields = EmployeeSerializer.Meta.read_only_fields + ['employee_id']


class EmployeeListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for employee lists.
    """
    full_name = serializers.ReadOnlyField()
    manager_name = serializers.CharField(source='manager.full_name', read_only=True)
    
    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'first_name', 'last_name', 'full_name',
            'email', 'department', 'position', 'status', 'manager_name',
            'hire_date', 'employment_type'
        ]


class EmployeeTerminationSerializer(serializers.Serializer):
    """
    Serializer for employee termination.
    """
    end_date = serializers.DateField()
    reason = serializers.CharField(max_length=500)
    
    def save(self, employee):
        """
        Terminate employee.
        """
        employee.terminate(
            end_date=self.validated_data['end_date'],
            reason=self.validated_data['reason']
        )
        return employee


class EmployeeHierarchySerializer(serializers.ModelSerializer):
    """
    Serializer for employee hierarchy/org chart.
    """
    full_name = serializers.ReadOnlyField()
    direct_reports = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'first_name', 'last_name', 'full_name',
            'position', 'department', 'direct_reports'
        ]
    
    def get_direct_reports(self, obj):
        """
        Get direct reports recursively.
        """
        direct_reports = obj.get_direct_reports()
        return EmployeeHierarchySerializer(direct_reports, many=True).data


class DepartmentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating departments.
    """
    class Meta:
        model = Department
        fields = [
            'name', 'code', 'description', 'parent',
            'head', 'budget', 'cost_center'
        ]
    
    def validate_code(self, value):
        """
        Validate department code uniqueness within tenant.
        """
        request = self.context.get('request')
        tenant_id = getattr(request, 'tenant_id', None)
        
        if tenant_id:
            queryset = Department.objects.filter(
                tenant_id=tenant_id,
                code=value
            )
            
            if self.instance:
                queryset = queryset.exclude(id=self.instance.id)
            
            if queryset.exists():
                raise serializers.ValidationError(
                    "Department code must be unique within the organization."
                )
        
        return value
    
    def create(self, validated_data):
        """
        Create department with tenant context.
        """
        request = self.context.get('request')
        tenant_id = getattr(request, 'tenant_id', None)
        
        if tenant_id:
            validated_data['tenant_id'] = tenant_id
        
        return super().create(validated_data)
