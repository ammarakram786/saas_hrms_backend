"""
Management command to create superuser with superuser role.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.accounts.models import User, Role


class Command(BaseCommand):
    help = 'Create superuser with superuser role'

    def add_arguments(self, parser):
        parser.add_argument('--email', required=True, help='Superuser email')
        parser.add_argument('--password', required=True, help='Superuser password')
        parser.add_argument('--first-name', required=True, help='Superuser first name')
        parser.add_argument('--last-name', required=True, help='Superuser last name')

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        first_name = options['first_name']
        last_name = options['last_name']

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.ERROR(f'User with email {email} already exists.')
            )
            return

        # Check if superuser role exists
        try:
            superuser_role = Role.objects.get(name='Superuser')
        except Role.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Superuser role not found. Please run create_superuser_role first.')
            )
            return

        with transaction.atomic():
            # Create superuser
            user = User.objects.create_superuser(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )

            # Assign superuser role
            user.roles.add(superuser_role)

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created superuser {email} with superuser role.'
                )
            )
