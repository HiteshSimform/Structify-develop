from celery import shared_task
from django.utils import timezone
from datetime import date, timedelta

from django.db import transaction
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings

from .models import Salary
from employees.models import Employees
from users.models import CustomUser
from .utils import calculate_salary_components


@shared_task
def generate_monthly_salaries():
    """
    Auto-generate salaries for all active employees for the current month.
    Unpaid leaves are considered in deductions using utility function.
    """
    today = timezone.now().date()
    start_date = date(today.year, today.month, 1)
    end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    system_user = CustomUser.objects.filter(is_superuser=True).first()

    with transaction.atomic():
        for employee in Employees.objects.filter(is_deleted=False):
            components = calculate_salary_components(employee, start_date, end_date)

            Salary.objects.create(
                employee=employee,
                basic_salary=components["basic_salary"],
                allowances=components["allowances"],
                deductions=components["deductions"],
                net_salary=components["net_salary"],
                pay_period_start=start_date,
                pay_period_end=end_date,
                payment_date=end_date,
                created_by=system_user,
                modified_by=system_user,
            )

    return "Monthly salaries generated successfully."