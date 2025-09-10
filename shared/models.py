from django.utils import timezone
from django.db import models
from .managers import SoftDeleteManager
import uuid
from django.db import models

class TimeStampedUUID(models.Model):
    pkid = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True,blank=True,db_index=True)

    objects = SoftDeleteManager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        if hasattr(self, "is_active"):  
            self.is_active = False
        self.save()


    def restore(self, using=None, keep_parents=False):
        self.is_deleted = False
        self.deleted_at = None
        if hasattr(self, "is_active"):
            self.is_active = False
        self.save()
    
    def hard_delete(self):
        super(SoftDeleteModel, self).delete()
    

