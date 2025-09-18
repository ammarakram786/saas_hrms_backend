#!/usr/bin/env python
"""
Django management command to create tenant_admin role with full permissions.
"""

from django.core.management.base import BaseCommand
from apps.accounts.models import Role, Permission


class Command(BaseCommand):
    help = 'Create tenant_admin role with full permissions for each tenant'

    def handle(self, *args, **options):
        """Create tenant_admin role with all permissions for each tenant."""
        
        # Get all permissions
        all_permissions = Permission.objects.all()
        
        if not all_permissions.exists():
            self.stdout.write(
                self.style.ERROR("No permissions found. Please run 'python manage.py seed_permissions' first.")
            )
            return
        
        # Get all tenants
        from apps.tenants.models import Tenant
        tenants = Tenant.objects.all()
        
        if not tenants.exists():
            self.stdout.write(
                self.style.ERROR("No tenants found. Please create a tenant first.")
            )
            return
        
        created_count = 0
        updated_count = 0
        
        # Create tenant_admin role for each tenant
        for tenant in tenants:
            role, created = Role.objects.get_or_create(
                name='tenant_admin',
                tenant_id=tenant.id,
                defaults={
                    'description': 'Tenant Administrator - Full access within tenant context',
                    'is_system': True,
                    'is_active': True,
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f"Created role: {role.name} for tenant: {tenant.name}")
            else:
                updated_count += 1
                self.stdout.write(f"Updated role: {role.name} for tenant: {tenant.name}")
            
            # Add all permissions to the role
            role.permissions.set(all_permissions)
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully processed {tenants.count()} tenants. "
                f"Created: {created_count}, Updated: {updated_count}"
            )
        )
        
        # Display role details for first tenant
        if tenants.exists():
            first_tenant = tenants.first()
            role = Role.objects.get(name='tenant_admin', tenant_id=first_tenant.id)
            self.stdout.write(f"\nRole Details (example for {first_tenant.name}):")
            self.stdout.write(f"Name: {role.name}")
            self.stdout.write(f"Description: {role.description}")
            self.stdout.write(f"Permissions: {role.permissions.count()}")
            self.stdout.write(f"System Role: {role.is_system}")
            self.stdout.write(f"Active: {role.is_active}")