"""
Department serializers.
"""
from rest_framework import serializers
from ..models import Department


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


class DepartmentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating Department.
    """
    
    class Meta:
        model = Department
        fields = [
            'name', 'code', 'description', 'parent', 'head',
            'budget', 'cost_center', 'is_active'
        ]
    
    def validate_code(self, value):
        """
        Validate department code uniqueness.
        """
        if Department.objects.filter(code=value).exists():
            raise serializers.ValidationError(
                "Department code must be unique."
            )
        return value
