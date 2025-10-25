from django.contrib import admin
from django.urls import reverse, path
from django.shortcuts import redirect
from django.utils import timezone
from datetime import timedelta
from .models import PremiumListing, PromoCode, EmailNotification
from properties.models import Property
from accounts.models import User
import uuid

@admin.register(PremiumListing)
class PremiumListingAdmin(admin.ModelAdmin):
    list_display = ('property', 'user', 'plan_type', 'start_date', 'end_date', 'is_active_display', 'amount_paid', 'days_remaining')
    list_filter = ('plan_type', 'is_active', 'start_date', 'end_date')
    search_fields = ('property__title', 'user__username', 'user__email')
    readonly_fields = ('start_date', 'end_date', 'amount_paid')
    actions = ['activate_premium', 'deactivate_premium', 'extend_premium', 'create_bulk_premium']
    list_per_page = 25

    fieldsets = (
        ('🎩 Basic Information', {
            'fields': ('property', 'user')
        }),
        ('💰 Premium Details', {
            'fields': ('plan_type', 'amount_paid', 'payment_id')
        }),
        ('⏰ Duration Settings', {
            'fields': ('start_date', 'end_date', 'is_active')
        }),
    )

    def is_active_display(self, obj):
        if obj.is_active:
            if obj.end_date >= timezone.now():
                days_left = (obj.end_date - timezone.now()).days
                if days_left <= 7:
                    return f'⚠️ Expiring Soon ({days_left}d)'
                else:
                    return '✅ Active'
            else:
                return '❌ Expired'
        else:
            return '⚪ Inactive'
    is_active_display.short_description = 'Status'
    is_active_display.admin_order_field = 'is_active'

    def days_remaining(self, obj):
        if obj.end_date >= timezone.now():
            days = (obj.end_date - timezone.now()).days
            return f"{days} days"
        else:
            return "Expired"
    days_remaining.short_description = 'Days Left'

    def activate_premium(self, request, queryset):
        count = queryset.update(is_active=True)
        # Update property premium status
        for listing in queryset:
            Property.objects.filter(id=listing.property.id).update(is_premium=True)
        self.message_user(request, f"✅ {count} premium listings activated.")
    activate_premium.short_description = "Activate selected premium listings"

    def deactivate_premium(self, request, queryset):
        count = queryset.update(is_active=False)
        # Update property premium status
        for listing in queryset:
            Property.objects.filter(id=listing.property.id).update(is_premium=False)
        self.message_user(request, f"⚪ {count} premium listings deactivated.")
    deactivate_premium.short_description = "Deactivate selected premium listings"

    def extend_premium(self, request, queryset):
        # Extend premium period by 30 days
        from datetime import timedelta
        count = 0
        for listing in queryset:
            listing.end_date += timedelta(days=30)
            listing.save()
            count += 1
        self.message_user(request, f"🗓️ Extended premium period (30 days) for {count} listings.")
    extend_premium.short_description = "Extend premium period (30 days)"

    def create_bulk_premium(self, request, queryset):
        # Create premium listings for selected properties
        success_count = 0
        already_exist = 0

        for property_obj in queryset:
            if PremiumListing.objects.filter(property=property_obj, is_active=True).exists():
                already_exist += 1
                continue

            # Create premium listing with default settings
            premium_listing = PremiumListing.objects.create(
                property=property_obj,
                user=property_obj.user,
                plan_type='basic',  # Default plan
                amount_paid=500,    # Default amount
                payment_id=f"ADMIN_BULK_{uuid.uuid4().hex[:8].upper()}",
                end_date=timezone.now() + timedelta(days=30),  # 30 days default
                is_active=True
            )
            # Update property premium status
            property_obj.is_premium = True
            property_obj.save()
            success_count += 1

        if success_count > 0:
            self.message_user(request, f"🎉 Created {success_count} new premium listings.")
        if already_exist > 0:
            self.message_user(request, f"⚠️ {already_exist} properties already had active premium status.")
    create_bulk_premium.short_description = "Create premium listing for selected properties"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('manual-create/', self.manual_create_premium, name='premium_premiumlisting_manual_create'),
        ]
        return custom_urls + urls

    def manual_create_premium(self, request):
        """Manual premium creation form for admin"""
        from django.template.loader import get_template
        from django.http import HttpResponse
        from django.template import RequestContext

        if request.method == 'POST':
            property_id = request.POST.get('property_id')
            user_id = request.POST.get('user_id')
            plan_type = request.POST.get('plan_type')
            amount_paid = request.POST.get('amount_paid')
            duration_days = int(request.POST.get('duration_days', 30))

            try:
                property_obj = Property.objects.get(id=property_id)
                user = User.objects.get(id=user_id)

                # Check if already has active premium
                existing = PremiumListing.objects.filter(property=property_obj, is_active=True).first()
                if existing:
                    self.message_user(request, f'⚠️ Property "{property_obj.title}" already has active premium status.',
                                    level='warning')
                    return redirect('secure_admin:premium_premiumlisting_changelist')

                # Create premium listing
                premium_listing = PremiumListing.objects.create(
                    property=property_obj,
                    user=user,
                    plan_type=plan_type,
                    amount_paid=amount_paid,
                    payment_id=f"ADMIN_MANUAL_{uuid.uuid4().hex[:8].upper()}",
                    end_date=timezone.now() + timedelta(days=duration_days),
                    is_active=True
                )

                # Update property premium status
                property_obj.is_premium = True
                property_obj.save()

                self.message_user(request, f'✅ Created premium listing for user "{user.username}"')
                return redirect('secure_admin:premium_premiumlisting_changelist')

            except (Property.DoesNotExist, User.DoesNotExist) as e:
                self.message_user(request, f'❌ Error: {str(e)}', level='error')

        # GET request - show manual creation form
        properties = Property.objects.select_related('user').order_by('-created_at')[:50]
        users = User.objects.filter(user_type='broker').order_by('username')

        context = {
            'properties': properties,
            'users': users,
            'plan_types': PremiumListing.PLAN_CHOICES,
            'title': 'Manually Create Premium Listing'
        }

        template = get_template('admin/premium_manual_create.html')
        return HttpResponse(template.render(context, request))


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'is_active', 'valid_from', 'valid_until', 'times_used', 'max_uses')
    list_filter = ('discount_type', 'is_active', 'created_at')
    search_fields = ('code',)
    readonly_fields = ('created_at', 'times_used')
    actions = ['deactivate_promo_codes']

    fieldsets = (
        ('🎫 Promo Code Details', {
            'fields': ('code', 'discount_type', 'discount_value')
        }),
        ('⏰ Validity Period', {
            'fields': ('valid_from', 'valid_until', 'max_uses')
        }),
        ('🔧 Admin Controls', {
            'fields': ('is_active', 'created_by')
        }),
        ('📊 Usage Statistics', {
            'fields': ('times_used', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    def deactivate_promo_codes(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f"⚪ {count} promo codes deactivated.")
    deactivate_promo_codes.short_description = "Deactivate selected promo codes"


@admin.register(EmailNotification)
class EmailNotificationAdmin(admin.ModelAdmin):
    list_display = ('notification_type', 'user', 'recipient_email', 'is_sent', 'sent_at', 'created_at')
    list_filter = ('notification_type', 'is_sent', 'created_at')
    search_fields = ('user__username', 'user__email', 'recipient_email')
    readonly_fields = ('created_at', 'sent_at')
    actions = ['resend_notifications']

    fieldsets = (
        ('📧 Notification Details', {
            'fields': ('user', 'notification_type', 'recipient_email')
        }),
        ('💬 Content', {
            'fields': ('subject', 'message')
        }),
        ('📡 Status', {
            'fields': ('is_sent', 'sent_at', 'error_message')
        }),
    )

    def resend_notifications(self, request, queryset):
        from django.core.mail import send_mail
        from django.conf import settings

        success_count = 0
        for notification in queryset.filter(is_sent=False):
            try:
                # Re-send email
                send_mail(
                    subject=notification.subject,
                    message=notification.message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[notification.recipient_email],
                    fail_silently=False,
                )
                notification.sent_at = timezone.now()
                notification.is_sent = True
                notification.save()
                success_count += 1
            except Exception as e:
                error_msg = f"Failed to resend: {str(e)}"
                notification.error_message = error_msg
                notification.save()

        if success_count > 0:
            self.message_user(request, f"📧 Successfully resent {success_count} notifications.")
    resend_notifications.short_description = "Resend selected notifications"
