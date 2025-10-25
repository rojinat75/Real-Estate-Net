from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from .models import EmailNotification
import logging

logger = logging.getLogger(__name__)


def send_premium_email(user, notification_type, property_obj=None, premium_listing=None, **extra_context):
    """
    Send premium-related emails to users

    Args:
        user: User instance
        notification_type: Type of notification (premium_activated, premium_expiring, etc.)
        property_obj: Property instance (optional)
        premium_listing: PremiumListing instance (optional)
        extra_context: Additional context variables
    """

    if notification_type not in settings.PREMIUM_EMAIL_SUBJECTS:
        logger.error(f"Unknown notification type: {notification_type}")
        return False

    try:
        # Get email templates from settings
        subject = settings.PREMIUM_EMAIL_SUBJECTS[notification_type]
        template = settings.PREMIUM_EMAIL_TEMPLATES[notification_type]

        # Build context
        context = {
            'user_name': user.get_full_name() or user.username,
            'user_email': user.email,
        }

        # Add property context if available
        if property_obj:
            context.update({
                'property_title': property_obj.title,
                'property_id': property_obj.id,
            })

        # Add premium listing context if available
        if premium_listing:
            context.update({
                'plan_type': premium_listing.plan_type,
                'amount_paid': premium_listing.amount_paid,
                'start_date': premium_listing.start_date.strftime('%B %d, %Y'),
                'end_date': premium_listing.end_date.strftime('%B %d, %Y'),
                'payment_id': premium_listing.payment_id,
                'days_remaining': premium_listing.days_remaining(),
            })

        # Add URL context
        context.update({
            'dashboard_url': f"{settings.SITE_URL}{reverse('accounts:dashboard')}",
            'plans_url': f"{settings.SITE_URL}{reverse('premium:premium_plans')}",
            'renewal_url': f"{settings.SITE_URL}{reverse('premium:premium_form')}?plan={premium_listing.plan_type if premium_listing else 'basic'}",
            'checkout_url': f"{settings.SITE_URL}{reverse('premium:premium_checkout', kwargs={'plan_type': premium_listing.plan_type if premium_listing else 'basic', 'property_pk': property_obj.id if property_obj else 0})}",
        })

        # Add extra context
        context.update(extra_context)

        # Format the message
        message = template.format(**context)

        # Send email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        # Log the email notification
        EmailNotification.objects.create(
            user=user,
            notification_type=notification_type,
            subject=subject,
            message=message,
            recipient_email=user.email,
            is_sent=True,
            sent_at=timezone.now(),
        )

        logger.info(f"Premium email sent successfully: {notification_type} to {user.email}")
        return True

    except Exception as e:
        # Log failed email
        EmailNotification.objects.create(
            user=user,
            notification_type=notification_type,
            subject=subject if 'subject' in locals() else "Email Send Failed",
            message=str(e),
            recipient_email=user.email,
            is_sent=False,
            error_message=str(e),
        )

        logger.error(f"Failed to send premium email {notification_type} to {user.email}: {str(e)}")
        return False


def send_bulk_notification(notification_type, users_with_properties):
    """
    Send bulk notifications to multiple users

    Args:
        notification_type: Type of notification
        users_with_properties: List of tuples (user, property, premium_listing)
    """
    success_count = 0
    total_count = len(users_with_properties)

    for user, property_obj, premium_listing in users_with_properties:
        if send_premium_email(user, notification_type, property_obj, premium_listing):
            success_count += 1

    return success_count, total_count


# Specific notification functions for common scenarios

def send_premium_activated_email(user, property_obj, premium_listing):
    """Send email when premium is activated"""
    return send_premium_email(
        user=user,
        notification_type='premium_activated',
        property_obj=property_obj,
        premium_listing=premium_listing,
        duration_days=(premium_listing.end_date - premium_listing.start_date).days
    )


def send_premium_expiring_email(user, property_obj, premium_listing):
    """Send reminder when premium is about to expire"""
    return send_premium_email(
        user=user,
        notification_type='premium_expiring',
        property_obj=property_obj,
        premium_listing=premium_listing,
        days_remaining=premium_listing.days_remaining()
    )


def send_premium_expired_email(user, property_obj, premium_listing):
    """Send notification when premium has expired"""
    return send_premium_email(
        user=user,
        notification_type='premium_expired',
        property_obj=property_obj,
        premium_listing=premium_listing
    )


def send_payment_received_email(user, property_obj, premium_listing):
    """Send confirmation when payment is received"""
    return send_premium_email(
        user=user,
        notification_type='payment_received',
        property_obj=property_obj,
        premium_listing=premium_listing
    )


def send_payment_failed_email(user, property_obj, plan_type, amount, payment_id):
    """Send notification when payment fails"""
    context = {
        'amount': amount,
        'payment_id': payment_id if payment_id else 'N/A'
    }

    # Create a temporary premium listing object for context
    class TempListing:
        def __init__(self, plan_type, payment_id):
            self.plan_type = plan_type
            self.payment_id = payment_id

    temp_listing = TempListing(plan_type, payment_id)

    return send_premium_email(
        user=user,
        notification_type='payment_failed',
        property_obj=property_obj,
        premium_listing=temp_listing,
        **context
    )
