from django.contrib import admin
from .models import Organization, AdminProfile


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_email', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'contact_email')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'organization', 'must_change_password', 'created_at')
    list_filter = ('role', 'organization', 'must_change_password')
    search_fields = ('user__username', 'user__email')
    autocomplete_fields = ('user',)