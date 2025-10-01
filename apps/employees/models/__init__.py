"""
Employee models package.
"""
from .employee import Employee
from .department import Department
from .employee_document import EmployeeDocument

__all__ = [
    'Employee',
    'Department', 
    'EmployeeDocument',
]
