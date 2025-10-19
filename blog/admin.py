from django.contrib import admin
from .models import BlogPost

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published_date', 'is_published', 'view_count')
    list_filter = ('is_published', 'published_date', 'author')
    search_fields = ('title', 'content', 'author__username')
    readonly_fields = ('published_date', 'updated_date', 'view_count')

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'author', 'excerpt')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('Media', {
            'fields': ('featured_image',)
        }),
        ('Publishing', {
            'fields': ('is_published',)
        }),
        ('Statistics', {
            'fields': ('view_count', 'published_date', 'updated_date'),
            'classes': ('collapse',)
        }),
    )

    actions = ['publish_posts', 'unpublish_posts', 'reset_view_counts']

    def publish_posts(self, request, queryset):
        queryset.update(is_published=True)
        self.message_user(request, f"{queryset.count()} posts published.")
    publish_posts.short_description = "Publish selected posts"

    def unpublish_posts(self, request, queryset):
        queryset.update(is_published=False)
        self.message_user(request, f"{queryset.count()} posts unpublished.")
    unpublish_posts.short_description = "Unpublish selected posts"

    def reset_view_counts(self, request, queryset):
        queryset.update(view_count=0)
        self.message_user(request, f"View counts reset for {queryset.count()} posts.")
    reset_view_counts.short_description = "Reset view counts for selected posts"
