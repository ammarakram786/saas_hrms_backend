"""
PayrollRecord serializers.
"""
from rest_framework import serializers
from ..models import PayrollRecord


class PayrollRecordSerializer(serializers.ModelSerializer):
    """
    Serializer for PayrollRecord model.
    """
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    payroll_period_name = serializers.CharField(source='payroll_period.name', read_only=True)
    
    class Meta:
        model = PayrollRecord
        fields = [
            'id', 'employee', 'employee_name', 'payroll_period', 'payroll_period_name',
            'base_salary', 'overtime_pay', 'allowances', 'bonuses',
            'tax', 'social_security', 'other_deductions',
            'gross_pay', 'total_deductions', 'net_pay', 'payslip_data',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'gross_pay', 'total_deductions', 'net_pay', 'created_at', 'updated_at']
