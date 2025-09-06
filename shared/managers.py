from django.utils import timezone 
from django.db import models


class SoftDeleteQuerySet(models.QuerySet):

    def delete(self):
        """Soft delete: mark as deleted, optionally deactivate if model has is_active."""
        update_kwargs = {"is_deleted": True, "deleted_at": timezone.now()}
        if hasattr(self.model, "is_active"):
            update_kwargs["is_active"] = False
        if hasattr(self.model, "is_verified"):
            update_kwargs["is_verified"] = False
        return super().update(**update_kwargs)

    def hard_delete(self):
        """Permanently delete records from the database."""
        return super().delete()

    def restore(self):
        """Restore soft-deleted records."""
        update_kwargs = {"is_deleted": False, "deleted_at": None}
        if hasattr(self.model, "is_active"):
            update_kwargs["is_active"] = True
        if hasattr(self.model, "is_verified"):
            update_kwargs["is_verified"] = True
        return super().update(**update_kwargs)

    def alive(self):
        """Return only non-deleted records."""
        return self.filter(is_deleted=False)

    def dead(self):
        """Return only soft-deleted records."""
        return self.filter(is_deleted=True)

    def all_with_deleted(self):
        """Return all records including soft-deleted."""
        return self.all()

    
    
class SoftDeleteManager(models.Manager):
    """Custom manager that uses the SoftDeleteQuerySet"""

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db)

    def alive(self):
        return self.get_queryset().alive()

    def dead(self):
        return self.get_queryset().dead()

    def hard_delete(self):
        return self.get_queryset().hard_delete()
    
    def all_with_deleted(self):
        return SoftDeleteQuerySet(self.model, using=self._db).all_with_deleted()

    def restore(self):
        return self.get_queryset().restore()
    
    def hard_delete(self):
        return self.get_queryset().hard_delete()

    def restore(self):
        return self.get_queryset().restore()