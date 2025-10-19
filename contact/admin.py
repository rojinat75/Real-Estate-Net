from django.contrib import admin
from .models import ContactInquiry

@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'property', 'inquiry_type', 'submitted_at', 'is_resolved')
    list_filter = ('inquiry_type', 'is_resolved', 'submitted_at')
    search_fields = ('name', 'email', 'phone', 'message', 'property__title')
    readonly_fields = ('submitted_at', 'updated_at')

    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Inquiry Details', {
            'fields': ('property', 'inquiry_type', 'message')
        }),
        ('Status', {
            'fields': ('is_resolved', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('submitted_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_resolved', 'mark_unresolved', 'export_inquiries']

    def mark_resolved(self, request, queryset):
        queryset.update(is_resolved=True)
        self.message_user(request, f"{queryset.count()} inquiries marked as resolved.")
    mark_resolved.short_description = "Mark selected inquiries as resolved"

    def mark_unresolved(self, request, queryset):
        queryset.update(is_resolved=False)
        self.message_user(request, f"{queryset.count()} inquiries marked as unresolved.")
    mark_unresolved.short_description = "Mark selected inquiries as unresolved"

    def export_inquiries(self, request, queryset):
        # This would typically export to CSV or Excel
        self.message_user(request, f"Export functionality would be implemented here for {queryset.count()} inquiries.")
    export_inquiries.short_description = "Export selected inquiries"
