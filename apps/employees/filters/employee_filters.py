"""
Employee filters.
"""
import django_filters
from django.db.models import Q
from ..models import Employee


class EmployeeFilter(django_filters.FilterSet):
    """
    Filter for Employee model.
    """
    # Text search
    search = django_filters.CharFilter(method='filter_search')
    
    # Status filters
    status = django_filters.ChoiceFilter(choices=Employee.STATUS_CHOICES)
    employment_type = django_filters.ChoiceFilter(choices=Employee.EMPLOYMENT_TYPE_CHOICES)
    
    # Department and position
    department = django_filters.CharFilter(field_name='department', lookup_expr='icontains')
    position = django_filters.CharFilter(field_name='position', lookup_expr='icontains')
    
    # Date filters
    hire_date_from = django_filters.DateFilter(field_name='hire_date', lookup_expr='gte')
    hire_date_to = django_filters.DateFilter(field_name='hire_date', lookup_expr='lte')
    start_date_from = django_filters.DateFilter(field_name='start_date', lookup_expr='gte')
    start_date_to = django_filters.DateFilter(field_name='start_date', lookup_expr='lte')
    
    # Salary filters
    base_salary_min = django_filters.NumberFilter(field_name='base_salary', lookup_expr='gte')
    base_salary_max = django_filters.NumberFilter(field_name='base_salary', lookup_expr='lte')
    
    # Manager filter
    manager = django_filters.ModelChoiceFilter(queryset=Employee.objects.all())
    has_manager = django_filters.BooleanFilter(field_name='manager', lookup_expr='isnull', exclude=True)
    
    # Gender filter
    gender = django_filters.CharFilter(field_name='gender', lookup_expr='iexact')
    
    # Ordering
    ordering = django_filters.OrderingFilter(
        fields=(
            ('first_name', 'first_name'),
            ('last_name', 'last_name'),
            ('employee_id', 'employee_id'),
            ('hire_date', 'hire_date'),
            ('base_salary', 'base_salary'),
            ('created_at', 'created_at'),
        ),
        field_labels={
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'employee_id': 'Employee ID',
            'hire_date': 'Hire Date',
            'base_salary': 'Base Salary',
            'created_at': 'Created Date',
        }
    )
    
    class Meta:
        model = Employee
        fields = {
            'employee_id': ['exact', 'icontains'],
            'email': ['exact', 'icontains'],
            'phone': ['exact', 'icontains'],
            'city': ['exact', 'icontains'],
            'state': ['exact', 'icontains'],
            'country': ['exact', 'icontains'],
        }
    
    def filter_search(self, queryset, name, value):
        """
        Search across multiple fields.
        """
        if not value:
            return queryset
        
        return queryset.filter(
            Q(first_name__icontains=value) |
            Q(last_name__icontains=value) |
            Q(employee_id__icontains=value) |
            Q(email__icontains=value) |
            Q(department__icontains=value) |
            Q(position__icontains=value)
        )
