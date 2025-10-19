from django.contrib import admin
from .models import PageView

@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ('url', 'user', 'ip_address', 'timestamp', 'user_agent')
    list_filter = ('timestamp', 'url')
    search_fields = ('url', 'user__username', 'ip_address')
    readonly_fields = ('timestamp', 'user_agent', 'ip_address', 'session_key')

    fieldsets = (
        ('Page Information', {
            'fields': ('url', 'user')
        }),
        ('Technical Details', {
            'fields': ('ip_address', 'user_agent', 'session_key')
        }),
        ('Timestamp', {
            'fields': ('timestamp',),
            'classes': ('collapse',)
        }),
    )

    actions = ['export_analytics', 'clear_old_views']

    def export_analytics(self, request, queryset):
        # This would typically export analytics data
        self.message_user(request, f"Export functionality would be implemented for {queryset.count()} page views.")
    export_analytics.short_description = "Export selected analytics data"

    def clear_old_views(self, request, queryset):
        # This would typically clear old analytics data
        self.message_user(request, f"Clear old data functionality would be implemented for {queryset.count()} records.")
    clear_old_views.short_description = "Clear selected old analytics data"
