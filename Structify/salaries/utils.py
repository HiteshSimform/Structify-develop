from decimal import Decimal, ROUND_HALF_UP
from calendar import monthrange
from leaves.models import LeaveApplication


def calculate_salary_components(employee, start_date, end_date):
    """
    Calculates salary breakdown for an employee considering:
    - Base salary, allowances, predefined deductions
    - Unpaid or half-day leaves (status='approved' and leave_type.is_paid=False)
    - Accurate daily rate based on total days in pay period

    Returns:
        dict: {
            "basic_salary",
            "allowances",
            "deductions",
            "net_salary",
            "leave_deduction",
            "unpaid_days",
        }
    """


    basic_salary = employee.salary or Decimal("0.00")
    allowances = employee.allowances or Decimal("0.00")
    deductions = employee.deductions or Decimal("0.00")


    unpaid_leaves = LeaveApplication.objects.filter(
        employee=employee,
        leave_type__is_paid=False,
        status="approved",
        is_deleted=False,
        start_date__lte=end_date,
        end_date__gte=start_date,
    )

    total_unpaid_days = Decimal("0.0")
    for leave in unpaid_leaves:
        actual_start = max(start_date, leave.start_date)
        actual_end = min(end_date, leave.end_date)
        days = (actual_end - actual_start).days + 1

        if hasattr(leave, "is_half_day") and leave.is_half_day:
            total_unpaid_days += Decimal(days) * Decimal("0.5")
        else:
            total_unpaid_days += Decimal(days)


    num_days_in_month = Decimal(str((end_date - start_date).days + 1))
    daily_rate = (basic_salary / num_days_in_month).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    leave_deduction = (total_unpaid_days * daily_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    total_deductions = (deductions + leave_deduction).quantize(Decimal("0.01"))
    net_salary = (basic_salary + allowances - total_deductions).quantize(Decimal("0.01"))

    return {
        "basic_salary": basic_salary,
        "allowances": allowances,
        "deductions": total_deductions,
        "net_salary": net_salary,
        "leave_deduction": leave_deduction,
        "unpaid_days": total_unpaid_days,
    }
