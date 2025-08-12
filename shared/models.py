# import uuid

# from django.db import models


# class TimeStampedModel(models.Model):
#     created_at = models.DateTimeField(auto_now_add=True, db_index=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         abstract = True


# class UUIDModel(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

#     class Meta:
#         abstract = True


# class SoftDeleteManager(models.Manager):
#     def get_queryset(self):
#         return super().get_queryset().filter(deleted_at__isnull=True)


# class SoftDeleteModel(models.Model):
#     deleted_at = models.DateTimeField(blank=True, null=True)

#     objects = SoftDeleteManager()
#     all_objects = models.Manager()
