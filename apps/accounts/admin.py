from django.contrib import admin
from django.utils import timezone
from .models import User  # import your custom user model


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'is_deleted', 'deleted_at')
    list_filter = ('is_active', 'is_deleted')
    search_fields = ('email', 'role',)

    actions = ['soft_delete_users', 'restore_users', 'deactivate_users', 'activate_users']

    def soft_delete_users(self, request, queryset):
        queryset.update(is_deleted=True, deleted_at=timezone.now(), is_active=False)
    soft_delete_users.short_description = "Soft delete selected users"

    def restore_users(self, request, queryset):
        queryset.update(is_deleted=False, deleted_at=None, is_active=True)
    restore_users.short_description = "Restore selected users"

    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_users.short_description = "Deactivate selected users"

    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
    activate_users.short_description = "Activate selected users"
