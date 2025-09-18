"""
Management command to seed default permissions and system roles.
"""
from django.core.management.base import BaseCommand
from apps.accounts.models import Permission


class Command(BaseCommand):
    help = 'Seed default permissions for the HRMS system'
    
    def handle(self, *args, **options):
        """
        Create default permissions.
        """
        permissions = [
            # Employee Management
            ('employee.view', 'employee', 'View employees'),
            ('employee.create', 'employee', 'Create employees'),
            ('employee.update', 'employee', 'Update employees'),
            ('employee.delete', 'employee', 'Delete employees'),
            ('employee.onboard', 'employee', 'Onboard employees'),
            ('employee.offboard', 'employee', 'Offboard employees'),
            
            # Attendance Management
            ('attendance.view', 'attendance', 'View attendance records'),
            ('attendance.create', 'attendance', 'Create attendance records'),
            ('attendance.update', 'attendance', 'Update attendance records'),
            ('attendance.delete', 'attendance', 'Delete attendance records'),
            ('attendance.shift.manage', 'attendance', 'Manage shifts'),
            ('attendance.clock.override', 'attendance', 'Override clock in/out'),
            
            # Leave Management
            ('leave.request', 'leave', 'Request leave'),
            ('leave.approve', 'leave', 'Approve leave requests'),
            ('leave.request_self', 'leave', 'Request own leave'),
            ('leave.view', 'leave', 'View leave records'),
            ('leave.manage_types', 'leave', 'Manage leave types'),
            
            # Payroll Management
            ('payroll.view', 'payroll', 'View payroll records'),
            ('payroll.create', 'payroll', 'Create payroll records'),
            ('payroll.configure', 'payroll', 'Configure payroll settings'),
            ('payroll.run', 'payroll', 'Run payroll processing'),
            ('payslip.view_self', 'payroll', 'View own payslip'),
            ('payslip.view_all', 'payroll', 'View all payslips'),
            
            # Employee Self-Service
            ('profile.update_self', 'profile', 'Update own profile'),
            ('profile.view_self', 'profile', 'View own profile'),
            
            # Admin/Tenant Management
            ('tenant.settings.update', 'tenant', 'Update tenant settings'),
            ('role.manage', 'role', 'Manage roles'),
            ('role.view', 'role', 'View roles'),
            ('user.invite', 'user', 'Invite users'),
            ('user.assign_roles', 'user', 'Assign roles to users'),
            ('user.manage', 'user', 'Manage users'),
            
            # Reporting
            ('reports.view', 'reports', 'View reports'),
            ('reports.export', 'reports', 'Export reports'),
            
            # System
            ('audit.view', 'audit', 'View audit logs'),
            ('system.admin', 'system', 'System administration'),
        ]
        
        created_count = 0
        
        for code, module, description in permissions:
            permission, created = Permission.objects.get_or_create(
                code=code,
                defaults={
                    'module': module,
                    'description': description
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created permission: {code}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} permissions'
            )
        )
