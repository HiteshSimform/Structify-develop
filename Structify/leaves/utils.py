from datetime import datetime
from django.utils import timezone
from .models import LeaveType, LeaveBalance


def allocate_leave_balances(employee, created_by):
    current_year = timezone.now().year
    for leave_type in LeaveType.objects.filter(is_deleted=False):
        if LeaveBalance.objects.filter(
            employee=employee, leave_type=leave_type, year=current_year
        ).exists():
            continue

        LeaveBalance.objects.create(
            employee=employee,
            leave_type=leave_type,
            balance_days=leave_type.max_days,
            year=current_year,
            created_by=created_by,
            modified_by=created_by,
        )
