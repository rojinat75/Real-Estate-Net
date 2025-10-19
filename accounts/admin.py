from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'phone_number', 'is_staff', 'is_active', 'date_joined', 'properties_count')
    list_filter = ('user_type', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'phone_number', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    fieldsets = UserAdmin.fieldsets + (
        ('Additional Information', {
            'fields': ('phone_number', 'address', 'user_type')
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Information', {
            'fields': ('phone_number', 'address', 'user_type')
        }),
    )

    def properties_count(self, obj):
        return obj.properties.count()
    properties_count.short_description = 'Properties Listed'

    actions = ['activate_users', 'deactivate_users', 'make_brokers', 'make_buyers']

    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} users activated.")
    activate_users.short_description = "Activate selected users"

    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} users deactivated.")
    deactivate_users.short_description = "Deactivate selected users"

    def make_brokers(self, request, queryset):
        queryset.update(user_type='broker')
        self.message_user(request, f"{queryset.count()} users set as brokers.")
    make_brokers.short_description = "Set selected users as brokers"

    def make_buyers(self, request, queryset):
        queryset.update(user_type='buyer')
        self.message_user(request, f"{queryset.count()} users set as buyers.")
    make_buyers.short_description = "Set selected users as buyers"
