#!/usr/bin/env python
"""
Django management command to seed default subscription plans.
"""

from django.core.management.base import BaseCommand
from apps.tenants.models import SubscriptionPlan


class Command(BaseCommand):
    help = 'Seed default subscription plans'

    def handle(self, *args, **options):
        """Create default subscription plans."""
        
        plans = [
            {
                'name': 'Free',
                'slug': 'free',
                'description': 'Perfect for small teams getting started',
                'price_monthly': 0.00,
                'price_yearly': 0.00,
                'max_users': 5,
                'max_employees': 25,
                'features': {
                    'time_tracking': True,
                    'leave_management': True,
                    'basic_reports': True,
                    'email_support': True,
                    'mobile_app': False,
                    'advanced_analytics': False,
                    'api_access': False,
                    'custom_branding': False,
                    'priority_support': False,
                },
                'is_active': True,
                'sort_order': 1
            },
            {
                'name': 'Basic',
                'slug': 'basic',
                'description': 'Essential features for growing businesses',
                'price_monthly': 29.99,
                'price_yearly': 299.99,
                'max_users': 25,
                'max_employees': 100,
                'features': {
                    'time_tracking': True,
                    'leave_management': True,
                    'basic_reports': True,
                    'email_support': True,
                    'mobile_app': True,
                    'advanced_analytics': False,
                    'api_access': True,
                    'custom_branding': False,
                    'priority_support': False,
                },
                'is_active': True,
                'sort_order': 2
            },
            {
                'name': 'Premium',
                'slug': 'premium',
                'description': 'Advanced features for established companies',
                'price_monthly': 79.99,
                'price_yearly': 799.99,
                'max_users': 100,
                'max_employees': 500,
                'features': {
                    'time_tracking': True,
                    'leave_management': True,
                    'basic_reports': True,
                    'email_support': True,
                    'mobile_app': True,
                    'advanced_analytics': True,
                    'api_access': True,
                    'custom_branding': True,
                    'priority_support': True,
                    'payroll_integration': True,
                    'performance_reviews': True,
                    'document_management': True,
                },
                'is_active': True,
                'sort_order': 3
            },
            {
                'name': 'Enterprise',
                'slug': 'enterprise',
                'description': 'Full-featured solution for large organizations',
                'price_monthly': 199.99,
                'price_yearly': 1999.99,
                'max_users': -1,  # Unlimited
                'max_employees': -1,  # Unlimited
                'features': {
                    'time_tracking': True,
                    'leave_management': True,
                    'basic_reports': True,
                    'email_support': True,
                    'mobile_app': True,
                    'advanced_analytics': True,
                    'api_access': True,
                    'custom_branding': True,
                    'priority_support': True,
                    'payroll_integration': True,
                    'performance_reviews': True,
                    'document_management': True,
                    'single_sign_on': True,
                    'advanced_security': True,
                    'dedicated_support': True,
                    'custom_integrations': True,
                    'white_label': True,
                },
                'is_active': True,
                'sort_order': 4
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for plan_data in plans:
            plan, created = SubscriptionPlan.objects.get_or_create(
                slug=plan_data['slug'],
                defaults=plan_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"Created plan: {plan.name}")
                )
            else:
                # Update existing plan
                for key, value in plan_data.items():
                    setattr(plan, key, value)
                plan.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f"Updated plan: {plan.name}")
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully processed {len(plans)} subscription plans. "
                f"Created: {created_count}, Updated: {updated_count}"
            )
        )
