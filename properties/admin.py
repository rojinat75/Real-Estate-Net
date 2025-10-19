from django.contrib import admin
from django.utils import timezone
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
    list_display = ('property', 'caption')
    list_filter = ('property',)
    search_fields = ('property__title', 'caption')

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
