from celery import shared_task
from .models import LeaveBalance
from django.utils import timezone
from users.models import CustomUser
from .utils import allocate_leave_balances


@shared_task
def carry_forward_leave_balances():
    current_year = timezone.now().year
    prev_year = current_year - 1

    previous_balances = LeaveBalance.objects.filter(year=prev_year, is_deleted=False)

    for balance in previous_balances:
        new_balance, created = LeaveBalance.objects.get_or_create(
            employee=balance.employee,
            leave_type=balance.leave_type,
            year=current_year,
            defaults={
                "balance_days": balance.balance_days,
                "created_by": balance.created_by,
                "modified_by": balance.modified_by,
            },
        )
        if not created:
            new_balance.balance_days += balance.balance_days
            new_balance.save()


@shared_task
def allocate_annual_leave_balances():
    for employee in CustomUser.objects.filter(role="Developer", is_active=True):
        allocate_leave_balances(employee=employee, created_by=employee)
