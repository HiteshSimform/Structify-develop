from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import LeaveApplication
from salaries.models import Salary
from decimal import Decimal
from django.utils.timezone import now
from datetime import timedelta


def calculate_unpaid_leave_days(employee, period_start, period_end):
    unpaid_leaves = LeaveApplication.objects.filter(
        employee=employee,
        leave_type__is_paid=False,
        status="Approved",
        start_date__lte=period_end,
        end_date__gte=period_start,
        is_deleted=False,
    )

    total_unpaid_days = 0
    for leave in unpaid_leaves:
        effective_start = max(leave.start_date, period_start)
        effective_end = min(leave.end_date, period_end)
        total_unpaid_days += (effective_end - effective_start).days + 1

    return total_unpaid_days


def refresh_salary(employee, leave_start, leave_end):
    salary_qs = Salary.objects.filter(
        employee=employee,
        is_deleted=False,
        pay_period_start__lte=leave_end,
        pay_period_end__gte=leave_start,
    )

    for salary in salary_qs:
        total_days = (salary.pay_period_end - salary.pay_period_start).days + 1
        unpaid_days = calculate_unpaid_leave_days(
            employee, salary.pay_period_start, salary.pay_period_end
        )

        if total_days > 0:
            per_day_salary = salary.basic_salary / Decimal(total_days)
            salary.deductions = per_day_salary * unpaid_days
            salary.net_salary = (
                salary.basic_salary + salary.allowances - salary.deductions
            )
            salary.modified_by = employee.user
            salary.save()


@receiver(post_save, sender=LeaveApplication)
def update_salary_on_leave_save(sender, instance, **kwargs):
    if instance.status == "Approved":
        refresh_salary(instance.employee, instance.start_date, instance.end_date)


@receiver(post_delete, sender=LeaveApplication)
def update_salary_on_leave_delete(sender, instance, **kwargs):
    refresh_salary(instance.employee, instance.start_date, instance.end_date)
