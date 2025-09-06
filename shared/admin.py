from django.contrib import admin

class SoftDeleteAdmin(admin.ModelAdmin):
    """Base admin for models with soft delete"""
    
    list_filter = ('is_deleted',)  # allow filtering by deletion status
    actions = ['soft_delete_selected', 'hard_delete_selected', 'restore_selected']

    def get_queryset(self, request):
        # Show all objects (including soft-deleted) in admin
        qs = super().get_queryset(request)
        return qs.all_with_deleted()  # requires SoftDeleteManager.all_with_deleted()

    # Soft delete selected
    def soft_delete_selected(self, request, queryset):
        queryset.delete()  # marks as deleted
    soft_delete_selected.short_description = "Soft delete selected records"

    # Hard delete selected
    def hard_delete_selected(self, request, queryset):
        queryset.hard_delete()  # permanently delete
    hard_delete_selected.short_description = "Hard delete selected records"

    # Restore selected
    def restore_selected(self, request, queryset):
        queryset.restore()  # restore soft-deleted
    restore_selected.short_description = "Restore selected records"
