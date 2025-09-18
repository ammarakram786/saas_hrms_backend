"""
Payroll serializers.
"""
from rest_framework import serializers
from .models import PayrollPeriod, PayrollRecord, PayrollComponent


class PayrollPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollPeriod
        fields = '__all__'


class PayrollRecordSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    
    class Meta:
        model = PayrollRecord
        fields = '__all__'


class PayrollComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollComponent
        fields = '__all__'
