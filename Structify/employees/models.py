from django.db import models
from users.models import CustomUser
from designations.models import Designation

# Create your models here.


class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_departments",
    )
    modified_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="modified_departments",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_deleted = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deleted_departments",
    )
    deleted_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    def __str__(self):
        return self.name


class Employees(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="employee"
    )  # reverse relation
    phone_number = models.CharField(max_length=15)
    hire_date = models.DateField()
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, related_name="employees"
    )
    designation = models.ForeignKey(
        Designation, on_delete=models.SET_NULL, null=True, related_name="employees"
    )

    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_employees",
    )
    modified_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="modified_employees",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_deleted = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deleted_employees",
    )
    deleted_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    def __str__(self):
        return self.user.name
