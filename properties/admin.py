from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render, redirect
from .models import Property, PropertyType, Amenity, Image, SavedSearch, Company, Location

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'property_type', 'city', 'state', 'price', 'status', 'is_premium', 'created_at', 'is_verified')
    list_filter = ('property_type', 'status', 'is_premium', 'created_at', 'state')
    search_fields = ('title', 'description', 'city', 'state', 'user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'description', 'property_type')
        }),
        ('Location', {
            'fields': ('address', 'city', 'state', 'zip_code', 'country')
        }),
        ('Property Details', {
            'fields': ('price', 'square_footage', 'lot_size', 'year_built', 'zoning', 'status')
        }),
        ('Contact Information', {
            'fields': ('broker_name', 'broker_email', 'broker_phone')
        }),
        ('Media', {
            'fields': ('virtual_tour_url', 'floor_plan_image')
        }),
        ('Verification & Status', {
            'fields': ('is_premium', 'is_verified')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def is_verified(self, obj):
        return "✅ Verified" if obj.user.is_staff or obj.user.is_superuser else "❌ Unverified"
    is_verified.short_description = "Verification Status"

    def company_name(self, obj):
        return obj.company.name if obj.company else "No Company"
    company_name.short_description = "Company"

    def location_name(self, obj):
        return obj.location.name if obj.location else "No Location"
    location_name.short_description = "Location"

    actions = ['mark_as_verified', 'mark_as_premium', 'remove_premium', 'export_properties', 'bulk_update_status']

    def mark_as_verified(self, request, queryset):
        queryset.update(is_verified=True)
        self.message_user(request, f"{queryset.count()} properties marked as verified.")
    mark_as_verified.short_description = "Mark selected properties as verified"

    def mark_as_premium(self, request, queryset):
        queryset.update(is_premium=True)
        self.message_user(request, f"{queryset.count()} properties marked as premium.")
    mark_as_premium.short_description = "Mark selected properties as premium"

    def remove_premium(self, request, queryset):
        queryset.update(is_premium=False)
        self.message_user(request, f"{queryset.count()} properties removed from premium.")
    remove_premium.short_description = "Remove premium status from selected properties"

    def export_properties(self, request, queryset):
        # Export selected properties to CSV
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="properties_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'

        writer = csv.writer(response)
        writer.writerow(['Title', 'User', 'Type', 'City', 'State', 'Price', 'Status', 'Premium', 'Verified', 'Created'])

        for property in queryset:
            writer.writerow([
                property.title,
                property.user.username,
                property.property_type.name if property.property_type else '',
                property.city,
                property.state,
                property.price,
                property.status,
                'Yes' if property.is_premium else 'No',
                'Yes' if property.is_verified else 'No',
                property.created_at.strftime('%Y-%m-%d %H:%M')
            ])

        self.message_user(request, f"Exported {queryset.count()} properties to CSV.")
    export_properties.short_description = "Export selected properties to CSV"

    def bulk_update_status(self, request, queryset):
        # Bulk update property status
        from django.contrib.admin.helpers import Fieldset
        from django import forms

        if 'apply' in request.POST:
            new_status = request.POST.get('status')
            queryset.update(status=new_status)
            self.message_user(request, f"Updated status to '{new_status}' for {queryset.count()} properties.")
            return

        # Show a form to select new status
        form = forms.Form()
        form.fields['status'] = forms.ChoiceField(
            choices=[('for_sale', 'For Sale'), ('for_lease', 'For Lease'), ('sold', 'Sold'), ('leased', 'Leased')],
            widget=forms.Select(attrs={'class': 'form-control'})
        )

        return self.render_change_form(request, {'form': form, 'selected_items': queryset})
    bulk_update_status.short_description = "Bulk update property status"

@admin.register(PropertyType)
class PropertyTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('image_thumbnail', 'property', 'caption', 'status', 'file_size_display', 'dimensions', 'is_fake_suspected', 'created_at')
    list_filter = ('status', 'is_duplicate', 'created_at', 'property__city', 'property__state')
    search_fields = ('property__title', 'caption', 'flagged_reason', 'moderation_notes')
    readonly_fields = ('created_at', 'updated_at', 'file_size', 'width', 'height', 'image_preview')
    actions = ['approve_images', 'reject_images', 'flag_for_review', 'soft_delete_images', 'mark_as_duplicate', 'restore_images']
    list_per_page = 25

    fieldsets = (
        ('📸 Image Information', {
            'fields': ('property', 'image', 'image_preview', 'caption')
        }),
        ('📊 Image Metadata', {
            'fields': ('file_size', 'width', 'height', 'dimensions'),
            'classes': ('collapse',)
        }),
        ('🚩 Moderation Status', {
            'fields': ('status', 'flagged_reason', 'flagged_by', 'flagged_at', 'moderation_notes', 'moderated_by', 'moderated_at')
        }),
        ('🗑️ Deletion Tracking', {
            'fields': ('deleted_at', 'deleted_by', 'deletion_reason'),
            'classes': ('collapse',)
        }),
        ('🔍 Duplicate Detection', {
            'fields': ('is_duplicate', 'duplicate_of'),
            'classes': ('collapse',)
        }),
        ('📅 Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def image_thumbnail(self, obj):
        """Display thumbnail image in admin list"""
        if obj.image:
            return f'<img src="{obj.image.url}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 4px;" />'
        return "No Image"
    image_thumbnail.short_description = "Image"
    image_thumbnail.allow_tags = True

    def image_preview(self, obj):
        """Display full-size image preview in admin detail"""
        if obj.image:
            return f'<img src="{obj.image.url}" style="max-width: 400px; max-height: 400px; object-fit: contain;" />'
        return "No Image"
    image_preview.short_description = "Image Preview"
    image_preview.allow_tags = True

    def file_size_display(self, obj):
        """Display human-readable file size"""
        if obj.file_size:
            size = obj.file_size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        return "Unknown"
    file_size_display.short_description = "Size"

    def dimensions(self, obj):
        """Display image dimensions"""
        if obj.width and obj.height:
            return f"{obj.width}×{obj.height}"
        return "Unknown"
    dimensions.short_description = "Dimensions"

    def is_fake_suspected(self, obj):
        """Display fake suspicion status"""
        if obj.is_fake_suspected():
            return "⚠️ Suspected"
        return "✅ OK"
    is_fake_suspected.short_description = "Fake Check"

    def approve_images(self, request, queryset):
        """Bulk approve selected images"""
        count = 0
        for image in queryset:
            if image.status != 'approved':
                image.approve_image(request.user)
                count += 1
        self.message_user(request, f"✅ Approved {count} images.")
    approve_images.short_description = "Approve selected images"

    def reject_images(self, request, queryset):
        """Bulk reject selected images"""
        count = 0
        for image in queryset:
            if image.status != 'rejected':
                image.reject_image(request.user, "Bulk rejection by admin")
                count += 1
        self.message_user(request, f"❌ Rejected {count} images.")
    reject_images.short_description = "Reject selected images"

    def flag_for_review(self, request, queryset):
        """Bulk flag images for review"""
        count = 0
        for image in queryset:
            if image.status != 'flagged':
                image.flag_for_review(request.user, "Bulk flagged for review")
                count += 1
        self.message_user(request, f"🚩 Flagged {count} images for review.")
    flag_for_review.short_description = "Flag selected images for review"

    def soft_delete_images(self, request, queryset):
        """Bulk soft delete images"""
        count = 0
        for image in queryset:
            if image.status != 'deleted':
                image.soft_delete(request.user, "Bulk deletion by admin")
                count += 1
        self.message_user(request, f"🗑️ Soft deleted {count} images.")
    soft_delete_images.short_description = "Soft delete selected images"

    def mark_as_duplicate(self, request, queryset):
        """Mark selected images as duplicates"""
        if len(queryset) < 2:
            self.message_user(request, "⚠️ Please select at least 2 images to mark as duplicates.", level='warning')
            return

        # Mark all but the first as duplicates of the first
        images_list = list(queryset)
        master_image = images_list[0]

        count = 0
        for image in images_list[1:]:
            image.is_duplicate = True
            image.duplicate_of = master_image
            image.save()
            count += 1

        self.message_user(request, f"📋 Marked {count} images as duplicates of {master_image}.")
    mark_as_duplicate.short_description = "Mark selected as duplicates"

    def restore_images(self, request, queryset):
        """Restore deleted images"""
        count = 0
        for image in queryset:
            if image.status == 'deleted':
                image.restore_image(request.user)
                count += 1
        self.message_user(request, f"🔄 Restored {count} images.")
    restore_images.short_description = "Restore selected images"

    def get_queryset(self, request):
        """Optimize queryset with select_related and prefetch_related"""
        return super().get_queryset(request).select_related(
            'property', 'flagged_by', 'moderated_by', 'deleted_by'
        )

    def save_model(self, request, obj, form, change):
        """Override save to ensure metadata is populated"""
        super().save_model(request, obj, form, change)
        # Trigger metadata population if image was uploaded
        if 'image' in form.changed_data:
            obj.save()  # Re-save to populate metadata

    def get_urls(self):
        """Add custom URLs for image moderation"""
        urls = super().get_urls()
        custom_urls = [
            path('review-queue/', self.image_review_queue, name='properties_image_review_queue'),
            path('fake-detection/', self.run_fake_detection, name='properties_fake_detection'),
        ]
        return custom_urls + urls

    def image_review_queue(self, request):
        """Display images flagged for review"""
        flagged_images = Image.objects.filter(status='flagged').select_related('property', 'flagged_by')

        context = {
            'title': 'Image Review Queue',
            'flagged_images': flagged_images,
            'total_flagged': flagged_images.count(),
        }
        return render(request, 'admin/properties/image_review_queue.html', context)

    def run_fake_detection(self, request):
        """Run fake image detection on all images"""
        from .utils import detect_fake_images

        if request.method == 'POST':
            # Run detection
            flagged_count = detect_fake_images()

            self.message_user(
                request,
                f"🔍 Fake detection complete. {flagged_count} images flagged for review."
            )
            return redirect('admin:properties_image_changelist')

        context = {
            'title': 'Run Fake Image Detection',
            'description': 'This will scan all property images and flag suspicious ones for review.',
        }
        return render(request, 'admin/properties/fake_detection.html', context)

@admin.register(SavedSearch)
class SavedSearchAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'alert_enabled', 'created_at')
    list_filter = ('alert_enabled', 'created_at')
    search_fields = ('name', 'user__username')

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'email', 'phone')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'logo', 'description')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'website', 'address')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['activate_companies', 'deactivate_companies']

    def activate_companies(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} companies activated.")
    activate_companies.short_description = "Activate selected companies"

    def deactivate_companies(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} companies deactivated.")
    deactivate_companies.short_description = "Deactivate selected companies"

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'state', 'country', 'is_active')
    list_filter = ('type', 'state', 'country', 'is_active')
    search_fields = ('name', 'state', 'country')

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'type', 'state', 'country')
        }),
        ('Geographic Data', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

    actions = ['activate_locations', 'deactivate_locations']

    def activate_locations(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} locations activated.")
    activate_locations.short_description = "Activate selected locations"

    def deactivate_locations(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} locations deactivated.")
    deactivate_locations.short_description = "Deactivate selected locations"
