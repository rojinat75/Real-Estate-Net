from django.contrib import admin
from django.forms import Textarea
from .models import LegalPage


@admin.register(LegalPage)
class LegalPageAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'updated_at']
    list_filter = ['updated_at']
    search_fields = ['title', 'slug', 'content']
    readonly_fields = ['updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug')
        }),
        ('Content', {
            'fields': ('content',),
            'classes': ('wide',)
        }),
        ('Metadata', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )

    formfield_overrides = {
        # Make the content field use a larger textarea
    }

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'content':
            kwargs['widget'] = Textarea(attrs={
                'rows': 25,
                'cols': 80,
                'style': 'font-family: monospace; font-size: 12px;'
            })
        return super().formfield_for_dbfield(db_field, **kwargs)
