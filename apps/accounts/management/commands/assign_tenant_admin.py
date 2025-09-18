#!/usr/bin/env python
"""
Django management command to assign tenant_admin role to a user.
"""

from django.core.management.base import BaseCommand
from apps.accounts.models import User, Role, UserRole


class Command(BaseCommand):
    help = 'Assign tenant_admin role to a user'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            required=True,
            help='Email of the user to assign tenant_admin role'
        )
        parser.add_argument(
            '--tenant-id',
            type=str,
            required=True,
            help='Tenant ID for the user'
        )

    def handle(self, *args, **options):
        """Assign tenant_admin role to a user."""
        
        email = options['email']
        tenant_id = options['tenant_id']
        
        try:
            # Get the user
            user = User.objects.get(email=email, tenant_id=tenant_id)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"User with email '{email}' not found in tenant '{tenant_id}'")
            )
            return
        
        try:
            # Get the tenant_admin role for this tenant
            role = Role.objects.get(name='tenant_admin', tenant_id=tenant_id)
        except Role.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"tenant_admin role not found for tenant '{tenant_id}'")
            )
            return
        
        # Check if user already has this role
        if UserRole.objects.filter(user=user, role=role).exists():
            self.stdout.write(
                self.style.WARNING(f"User '{email}' already has tenant_admin role")
            )
            return
        
        # Assign the role
        UserRole.objects.create(
            user=user,
            role=role,
            assigned_by=user  # Self-assigned for now
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully assigned tenant_admin role to '{email}' for tenant '{tenant_id}'"
            )
        )
        
        # Display user details
        self.stdout.write(f"\nUser Details:")
        self.stdout.write(f"Name: {user.first_name} {user.last_name}")
        self.stdout.write(f"Email: {user.email}")
        self.stdout.write(f"Tenant: {tenant_id}")
        self.stdout.write(f"Active: {user.is_active}")
        self.stdout.write(f"Roles: {user.roles.count()}")
