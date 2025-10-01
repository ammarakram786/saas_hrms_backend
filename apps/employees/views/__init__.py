"""
Employee views package.
"""
from .employee_views import EmployeeViewSet
from .department_views import DepartmentViewSet
from .employee_document_views import EmployeeDocumentViewSet

__all__ = [
    'EmployeeViewSet',
    'DepartmentViewSet',
    'EmployeeDocumentViewSet',
]
