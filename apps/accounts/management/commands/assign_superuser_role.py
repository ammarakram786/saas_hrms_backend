"""
Management command to assign superuser role to existing superusers.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.accounts.models import User, Role


class Command(BaseCommand):
    help = 'Assign superuser role to existing superusers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            help='Email of specific superuser to assign role to',
        )

    def handle(self, *args, **options):
        email = options.get('email')
        
        # Check if superuser role exists
        try:
            superuser_role = Role.objects.get(name='Superuser')
        except Role.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Superuser role not found. Please run create_superuser_role first.')
            )
            return

        # Get superusers to update
        if email:
            try:
                superusers = [User.objects.get(email=email, is_superuser=True)]
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Superuser with email {email} not found.')
                )
                return
        else:
            superusers = User.objects.filter(is_superuser=True)

        if not superusers:
            self.stdout.write(
                self.style.WARNING('No superusers found.')
            )
            return

        with transaction.atomic():
            updated_count = 0
            for user in superusers:
                if not user.roles.filter(name='Superuser').exists():
                    user.roles.add(superuser_role)
                    updated_count += 1
                    self.stdout.write(f'Assigned superuser role to {user.email}')

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully assigned superuser role to {updated_count} superusers.'
                )
            )
