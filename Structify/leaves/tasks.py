from celery import shared_task
from django.utils import timezone
from .models import LeaveBalance
from users.models import CustomUser


@shared_task
def carry_forward_leave_balances():
    current_year = timezone.now().year
    previous_year = current_year - 1

    prev_balances = LeaveBalance.objects.filter(year=previous_year, is_deleted=False)

    for balance in prev_balances:
        if not balance.leave_type.is_paid:
            continue

        new_balance, created = LeaveBalance.objects.get_or_create(
            employee=balance.employee,
            leave_type=balance.leave_type,
            year=current_year,
            defaults={
                "balance_days": 0,
                "created_by": balance.created_by,
                "modified_by": balance.modified_by,
            },
        )

        if not created:
            new_balance.balance_days += balance.balance_days
        else:
            new_balance.balance_days = balance.balance_days

        new_balance.save()
