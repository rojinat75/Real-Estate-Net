from django.contrib import admin
from django.urls import reverse, path
from django.shortcuts import redirect
from django.utils import timezone
from datetime import timedelta
from .models import PremiumListing
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
            path('manual-create/', self.manual_create_premium, name='manual_create_premium'),
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
                    return redirect('admin:premium_premiumlisting_changelist')

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
                return redirect('admin:premium_premiumlisting_changelist')

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
