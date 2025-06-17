from django.db import models
from users.models import CustomUser
from django.utils import timezone

# Create your models here.


class Designation(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_designations",
    )
    modified_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="modified_designations",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_deleted = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deleted_designations",
    )
    deleted_at = models.DateTimeField(null=True, blank=True, auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

# # designations/models.py
# from django.db import models
# from django.utils import timezone
# from users.models import CustomUser


# class ActiveDesignationManager(models.Manager):
#     """Hide soft‑deleted rows by default."""
#     def get_queryset(self):
#         return super().get_queryset().filter(is_deleted=False)


# class Designation(models.Model):
#     name = models.CharField(max_length=100, unique=True)
#     description = models.TextField(blank=True)

#     created_by  = models.ForeignKey(CustomUser, on_delete=models.SET_NULL,
#                                     null=True, related_name="created_designations")
#     modified_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL,
#                                     null=True, related_name="modified_designations")

#     created_at  = models.DateTimeField(auto_now_add=True)
#     updated_at  = models.DateTimeField(auto_now=True)

#     # soft delete
#     is_deleted  = models.BooleanField(default=False)
#     deleted_by  = models.ForeignKey(CustomUser, on_delete=models.SET_NULL,
#                                     null=True, blank=True, related_name="deleted_designations")
#     deleted_at  = models.DateTimeField(null=True, blank=True)

#     # managers
#     objects      = ActiveDesignationManager()          # default
#     all_objects  = models.Manager()                    # include deleted

#     class Meta:
#         ordering = ["name"]
#         verbose_name = "Designation"
#         verbose_name_plural = "Designations"

#     def delete(self, using=None, keep_parents=False):
#         """Soft delete override."""
#         self.is_deleted = True
#         self.deleted_at = timezone.now()
#         super().save(update_fields=["is_deleted", "deleted_at"])

#     def __str__(self) -> str:
#         return self.name
