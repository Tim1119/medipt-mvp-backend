from django.utils import timezone 
from django.db import models


class SoftDeleteQuerySet(models.QuerySet):

    def delete(self):
        return super().update(is_deleted=True,deleted_at=timezone.now(),is_active=False if hasattr(self.model, "is_active") else models.F("is_deleted"))
    
    def hard_delete(self):
        return super().delete()

    def alive(self):
        return self.filter(is_deleted=False)

    def dead(self):
        return self.filter(is_deleted=True)
    
    
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