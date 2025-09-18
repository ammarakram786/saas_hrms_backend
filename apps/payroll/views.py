"""
Payroll views.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import PayrollPeriod, PayrollRecord, PayrollComponent
from .serializers import PayrollPeriodSerializer, PayrollRecordSerializer, PayrollComponentSerializer


class PayrollPeriodViewSet(viewsets.ModelViewSet):
    serializer_class = PayrollPeriodSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if hasattr(self.request, 'tenant_id'):
            return PayrollPeriod.objects.filter(tenant_id=self.request.tenant_id)
        return PayrollPeriod.objects.none()


class PayrollRecordViewSet(viewsets.ModelViewSet):
    serializer_class = PayrollRecordSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if hasattr(self.request, 'tenant_id'):
            return PayrollRecord.objects.filter(tenant_id=self.request.tenant_id)
        return PayrollRecord.objects.none()


class PayrollComponentViewSet(viewsets.ModelViewSet):
    serializer_class = PayrollComponentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if hasattr(self.request, 'tenant_id'):
            return PayrollComponent.objects.filter(tenant_id=self.request.tenant_id)
        return PayrollComponent.objects.none()
