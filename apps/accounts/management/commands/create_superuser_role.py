"""
Management command to create superuser role with all permissions.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.accounts.models import Role, Permission


class Command(BaseCommand):
    help = 'Create superuser role with all permissions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force creation even if role already exists',
        )

    def handle(self, *args, **options):
        force = options['force']
        
        # Check if superuser role already exists
        if Role.objects.filter(name='Superuser').exists() and not force:
            self.stdout.write(
                self.style.WARNING('Superuser role already exists. Use --force to recreate.')
            )
            return

        with transaction.atomic():
            # Delete existing superuser role if force is used
            if force and Role.objects.filter(name='Superuser').exists():
                Role.objects.filter(name='Superuser').delete()
                self.stdout.write('Deleted existing superuser role.')

            # Get all permissions
            all_permissions = Permission.objects.all()
            
            if not all_permissions.exists():
                self.stdout.write(
                    self.style.ERROR('No permissions found. Please run seed_permissions first.')
                )
                return

            # Create superuser role
            superuser_role = Role.objects.create(
                name='Superuser',
                description='Superuser role with all permissions'
            )

            # Assign all permissions to superuser role
            superuser_role.permissions.set(all_permissions)

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created superuser role with {all_permissions.count()} permissions.'
                )
            )
