from django.db import models
from employees.models import Employees
from users.models import CustomUser


class Salary(models.Model):
    """
    Model representing monthly salary details of an employee,
    including breakdowns for allowances, deductions, net, and payment period.
    """

    employee = models.ForeignKey(
        Employees,
        on_delete=models.CASCADE,
        related_name="salaries",
        help_text="The employee this salary record belongs to.",
    )
    basic_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="The base salary for the employee before allowances and deductions.",
    )
    allowances = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Additional allowances provided to the employee.",
    )
    deductions = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Total deductions including unpaid leave, tax, etc.",
    )
    net_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Final amount paid to the employee after deductions.",
    )

    pay_period_start = models.DateField(
        help_text="Start date of the salary payment period."
    )
    pay_period_end = models.DateField(
        help_text="End date of the salary payment period."
    )
    payment_date = models.DateField(
        help_text="Date when the salary was paid or is to be paid."
    )

    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_salaries",
        help_text="User who created the record.",
    )
    modified_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="modified_salaries",
        help_text="User who last modified the record.",
    )

    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Timestamp when the record was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="Timestamp of last update."
    )

    is_deleted = models.BooleanField(default=False, help_text="Soft delete flag.")
    deleted_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deleted_salaries",
        help_text="User who deleted the record (soft delete).",
    )
    deleted_at = models.DateTimeField(
        null=True, blank=True, help_text="Time when record was soft-deleted."
    )

    class Meta:
        ordering = ["-payment_date"]
        verbose_name = "Salary"
        verbose_name_plural = "Salaries"
        unique_together = ["employee", "pay_period_start", "pay_period_end"]

    def __str__(self):
        return f"{self.employee.user.name} - {self.payment_date.strftime('%B %Y')} - ₹{self.net_salary}"
