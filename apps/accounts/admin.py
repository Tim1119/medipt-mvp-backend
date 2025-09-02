from django.contrib import admin
from django.utils import timezone
from .models import User 
from django.utils.translation import gettext_lazy as _ 


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email','id', 'is_active','is_verified', 'is_deleted', 'deleted_at')
    list_filter = ('role', 'is_active', 'is_verified', 'is_staff', 'created_at')
    ordering = ('-created_at',)
    readonly_fields = ('id','created_at', 'updated_at')
    # search_fields = ('email', 'role',)

    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        (_('Role & Status'), {
            'fields': ('role', 'is_active', 'is_verified', 'is_invited', 'is_staff')
        }),
        (_('Permissions'), {
            'fields': ('is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'created_at', 'updated_at')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'is_active', 'is_staff'),
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        """Make certain fields readonly after creation"""
        if obj:  # editing an existing object
            return self.readonly_fields + ('email',)
        return self.readonly_fields

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of superuser accounts"""
        if obj and obj.is_superuser:
            return False
        return super().has_delete_permission(request, obj)
    
    def get_list_display(self, request):
        """Add custom columns based on user role"""
        list_display = list(super().get_list_display(request))
        list_display.extend(['get_name'])
        return list_display

    @admin.display(description=_('Name'))
    def get_name(self, obj):
        return obj.full_name

    @admin.action(description=_('Activate selected users'),)
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} users were successfully activated.')


    @admin.action(description=_('Soft delete selected users'),)
    def soft_delete_users(self, request, queryset):
        updated = queryset.update(is_deleted=True, deleted_at=timezone.now(), is_active=False)
        self.message_user(request, f'{updated} users were soft deleted.')

    @admin.action(description=_('Restore selected users'),)
    def restore_users(self, request, queryset):
        updated = queryset.update(is_deleted=False, deleted_at=None, is_active=True)
        self.message_user(request, f'{updated} users were restored.')

    @admin.action(description=_('Deactivate selected users'),)
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} users were deactivated.')

    @admin.action(description=_('activate selected users'),)
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} users were activated.')
