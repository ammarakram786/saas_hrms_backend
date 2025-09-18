#!/usr/bin/env python
"""
Django management command to create a sample tenant for testing.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.tenants.models import Tenant, SubscriptionPlan


class Command(BaseCommand):
    help = 'Create a sample tenant for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--name',
            type=str,
            default='Sample Company',
            help='Name of the tenant'
        )
        parser.add_argument(
            '--plan',
            type=str,
            default='basic',
            choices=['free', 'basic', 'premium', 'enterprise'],
            help='Subscription plan'
        )

    def handle(self, *args, **options):
        """Create a sample tenant."""
        
        name = options['name']
        plan_slug = options['plan']
        
        # Get the subscription plan
        try:
            subscription_plan = SubscriptionPlan.objects.get(slug=plan_slug)
        except SubscriptionPlan.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"Subscription plan '{plan_slug}' not found.")
            )
            return
        
        # Create tenant
        tenant = Tenant.objects.create(
            name=name,
            slug=name.lower().replace(' ', '-'),
            plan=plan_slug,
            status='active',
            subscription_plan=subscription_plan,
            subscription_status='active',
            subscription_start_date=timezone.now(),
            subscription_end_date=timezone.now() + timedelta(days=365),
            contact_email=f'admin@{name.lower().replace(" ", "")}.com',
            contact_phone='+1-555-0123',
            address='123 Business St, City, State 12345',
            billing_email=f'billing@{name.lower().replace(" ", "")}.com',
            billing_address='123 Business St, City, State 12345',
            max_users=subscription_plan.max_users,
            max_employees=subscription_plan.max_employees,
        )
        
        # Initialize settings
        tenant.initialize_settings()
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created tenant '{tenant.name}' with {plan_slug} plan.\n"
                f"Tenant ID: {tenant.id}\n"
                f"Slug: {tenant.slug}\n"
                f"Contact Email: {tenant.contact_email}\n"
                f"Max Users: {tenant.max_users}\n"
                f"Max Employees: {tenant.max_employees}"
            )
        )
