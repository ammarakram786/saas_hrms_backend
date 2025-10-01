"""
Management command to setup superuser role system.
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import transaction
from apps.accounts.models import Role, Permission


class Command(BaseCommand):
    help = 'Setup superuser role system - create role and assign to existing superusers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreation of superuser role',
        )

    def handle(self, *args, **options):
        force = options['force']
        
        self.stdout.write('Setting up superuser role system...')
        
        # Step 1: Check if permissions exist
        if not Permission.objects.exists():
            self.stdout.write('Seeding permissions...')
            call_command('seed_permissions')
        
        # Step 2: Create superuser role
        self.stdout.write('Creating superuser role...')
        call_command('create_superuser_role', force=force)
        
        # Step 3: Assign superuser role to existing superusers
        self.stdout.write('Assigning superuser role to existing superusers...')
        call_command('assign_superuser_role')
        
        self.stdout.write(
            self.style.SUCCESS('Superuser role system setup completed successfully!')
        )
        
        # Display instructions
        self.stdout.write('\n' + '='*60)
        self.stdout.write('SUPERUSER ROLE SYSTEM SETUP COMPLETE')
        self.stdout.write('='*60)
        self.stdout.write('\nTo create new superusers, use:')
        self.stdout.write('python manage.py create_superuser --email admin@example.com --password yourpassword --first-name Admin --last-name User')
        self.stdout.write('\nTo assign superuser role to existing superusers:')
        self.stdout.write('python manage.py assign_superuser_role')
        self.stdout.write('\nRegular users can be created via API endpoints.')
        self.stdout.write('='*60)
