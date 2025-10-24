from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from ...models import PremiumListing
from ... import utils
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Manage premium subscriptions - send expiry reminders and deactivate expired listings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))

        now = timezone.now()

        # 1. Send reminders for listings expiring soon (7 days)
        self.stdout.write(self.style.SUCCESS('1. Processing expiry reminders...'))
        expiring_soon = PremiumListing.objects.filter(
            is_active=True,
            end_date__lte=now + timedelta(days=7),
            end_date__gt=now
        )

        reminder_count = 0
        for listing in expiring_soon:
            days_left = (listing.end_date - now).days

            # Only send reminder once (when 7 days remaining)
            if days_left <= 7 and days_left > 6:
                if dry_run:
                    self.stdout.write(f"  Would send expiry reminder: {listing.property.title} - {days_left} days")
                else:
                    if utils.send_premium_expiring_email(listing.user, listing.property, listing):
                        reminder_count += 1
                        self.stdout.write(f"  Sent expiry reminder: {listing.property.title} - {days_left} days")

        self.stdout.write(self.style.SUCCESS(f'Sent {reminder_count} expiry reminders'))

        # 2. Expire listings that have passed their end date
        self.stdout.write(self.style.SUCCESS('2. Processing expired listings...'))
        expired_listings = PremiumListing.objects.filter(
            is_active=True,
            end_date__lte=now
        )

        expired_count = 0
        for listing in expired_listings:
            if dry_run:
                self.stdout.write(f"  Would expire: {listing.property.title} - Expired on {listing.end_date}")
            else:
                # Deactivate premium listing
                listing.is_active = False
                listing.save()

                # Update property premium status
                listing.property.is_premium = False
                listing.property.save()

                # Send expiry notification
                utils.send_premium_expired_email(listing.user, listing.property, listing)

                expired_count += 1
                self.stdout.write(f"  Expired listing: {listing.property.title}")

        self.stdout.write(self.style.SUCCESS(f'Expired {expired_count} listings'))

        # 3. Show summary statistics
        self.stdout.write(self.style.SUCCESS('3. Subscription Statistics:'))

        total_active = PremiumListing.objects.filter(is_active=True).count()
        total_expired = PremiumListing.objects.filter(is_active=False).count()
        expiring_soon_count = expiring_soon.count()

        self.stdout.write(f'  Active subscriptions: {total_active}')
        self.stdout.write(f'  Expired subscriptions: {total_expired}')
        self.stdout.write(f'  Expiring soon (7 days): {expiring_soon_count}')

        # 4. Show upcoming expirations
        self.stdout.write(self.style.SUCCESS('4. Upcoming Expirations (next 30 days):'))
        upcoming = PremiumListing.objects.filter(
            is_active=True,
            end_date__lte=now + timedelta(days=30),
            end_date__gt=now
        ).order_by('end_date')[:10]  # Show next 10

        for listing in upcoming:
            days_left = (listing.end_date.date() - now.date()).days
            self.stdout.write(self.style.WARNING(
                f'  {listing.property.title} by {listing.user.username} - expires in {days_left} days'
            ))

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes were made'))
        else:
            self.stdout.write(self.style.SUCCESS('Subscription management complete!'))
