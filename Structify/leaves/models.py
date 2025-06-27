from django.db import models

# Create your models here.
from employees.models import Employees
from users.models import CustomUser
from django.core.exceptions import ValidationError
from django.utils import timezone


class LeaveType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_paid = models.BooleanField(default=True)
    max_days = models.PositiveIntegerField()

    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_leave_types",
    )
    modified_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="modified_leave_types",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_deleted = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deleted_leave_types",
    )
    deleted_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    def __str__(self):
        return self.name


class LeaveApplication(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    ]

    employee = models.ForeignKey(
        Employees, on_delete=models.CASCADE, related_name="leave_applications"
    )
    leave_type = models.ForeignKey(
        LeaveType, on_delete=models.CASCADE, related_name="applications"
    )
    start_date = models.DateField()
    end_date = models.DateField()
    leave_days = models.PositiveIntegerField(default=1)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    approver = models.ForeignKey(
        Employees,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_leaves",
    )

    status_changed_by = models.ForeignKey(
        CustomUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="leave_status_changers",
    )
    status_changed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_leave_applications",
    )
    modified_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="modified_leave_applications",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_deleted = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deleted_leave_applications",
    )
    deleted_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError("Start date cannot be after end date.")

        if self.start_date < timezone.now().date():
            raise ValidationError("Leave cannot start in the past.")

        overlapping = (
            LeaveApplication.objects.filter(
                employee=self.employee,
                start_date__lte=self.end_date,
                end_date__gte=self.start_date,
                is_deleted=False,
            )
            .exclude(pk=self.pk)
            .exists()
        )

        if overlapping:
            raise ValidationError("An overlapping leave already exists.")

    def save(self, *args, **kwargs):
        self.leave_days = (self.end_date - self.start_date).days + 1
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.user.name} - {self.status} ({self.start_date} to {self.end_date})"


class LeaveBalance(models.Model):
    employee = models.ForeignKey(
        Employees, on_delete=models.CASCADE, related_name="leave_balances"
    )
    leave_type = models.ForeignKey(
        LeaveType, on_delete=models.CASCADE, related_name="leave_balances"
    )
    balance_days = models.DecimalField(max_digits=5, decimal_places=2)
    year = models.PositiveIntegerField()

    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_leave_balances",
    )
    modified_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="modified_leave_balances",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_deleted = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deleted_leave_balances",
    )
    deleted_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    def __str__(self):
        return f"{self.employee.user.name} - {self.leave_type.name}"
