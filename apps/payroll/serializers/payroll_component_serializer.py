"""
PayrollComponent serializers.
"""
from rest_framework import serializers
from ..models import PayrollComponent


class PayrollComponentSerializer(serializers.ModelSerializer):
    """
    Serializer for PayrollComponent model.
    """
    
    class Meta:
        model = PayrollComponent
        fields = [
            'id', 'name', 'code', 'component_type', 'calculation_method',
            'is_taxable', 'is_mandatory', 'is_active',
            'fixed_amount', 'percentage_value', 'formula',
            'created_at', 'updated_at'
        ]
