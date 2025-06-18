# from rest_framework import serializers
# from .models import Salary
# from employees.serializers import PublicDepartmentSerializer, BasicEmployeeSerializer
# from users.serializers import CustomUserSerializer


# class SalarySerializer(serializers.ModelSerializer):
#     employee = BasicEmployeeSerializer(read_only=True)
#     created_by = CustomUserSerializer(read_only=True)
#     modified_by = CustomUserSerializer(read_only=True)
#     deleted_by = CustomUserSerializer(read_only=True)

#     class Meta:
#         model = Salary
#         fields = "__all__"
#         read_only_fields = [
#             "created_by",
#             "modified_by",
#             "created_at",
#             "updated_at",
#             "deleted_by",
#             "deleted_at",
#             "is_deleted",
#         ]


# class SalaryCreateUpdateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Salary
#         fields = [
#             "employee",
#             "basic_salary",
#             "allowances",
#             "deductions",
#             "net_salary",
#             "pay_period_start",
#             "pay_period_end",
#             "payment_date",
#         ]

#         def validate(self, data):
#             if data["pay_period_start"] > data["pay_period_end"]:
#                 raise serializers.ValidationError(
#                     "start date can not be after end date."
#                 )
#             if (
#                 data["net_salary"]
#                 != data["basic_salary"] + data["allowances"] - data["deductions"]
#             ):
#                 raise serializers.ValidationError(
#                     "Net salary does not match the expected calculation: basic + allowances - deductions."
#                 )
#             return data


# class DepartmentSalarySummarySerializer(serializers.Serializer):
#     department = serializers.CharField()
#     employee_count = serializers.IntegerField()
#     total_gross_salary = serializers.DecimalField(max_digits=12, decimal_places=2)
#     total_net_salary = serializers.DecimalField(max_digits=12, decimal_places=2)
#     total_deductions = serializers.DecimalField(max_digits=12, decimal_places=2)
#     average_net_salary = serializers.DecimalField(max_digits=12, decimal_places=2)
#     min_net_salary = serializers.DecimalField(max_digits=12, decimal_places=2)
#     max_net_salary = serializers.DecimalField(max_digits=12, decimal_places=2)
#     last_payment_date = serializers.DateField()


# class DepartmentExpenseSerializer(serializers.Serializer):
#     department = serializers.CharField()
#     employee_count = serializers.IntegerField()
#     total_expense = serializers.DecimalField(max_digits=12, decimal_places=2)


from datetime import date
from decimal import Decimal

from rest_framework import serializers
from .models import Salary
from employees.serializers import BasicEmployeeSerializer
from users.serializers import CustomUserSerializer
from leaves.models import LeaveApplication


# ────────────────────────────────────────────────────────────────────
# Helper
# ────────────────────────────────────────────────────────────────────
def unpaid_leave_days(employee, period_start, period_end):
    """
    Count unpaid leave days (leave_type.is_paid == False) that overlap the period.
    """
    leaves = LeaveApplication.objects.filter(
        employee=employee,
        status="Approved",
        leave_type__is_paid=False,
        is_deleted=False,
        start_date__lte=period_end,
        end_date__gte=period_start,
    )

    days = 0
    for lv in leaves:
        overlap_start = max(lv.start_date, period_start)
        overlap_end   = min(lv.end_date, period_end)
        days += (overlap_end - overlap_start).days + 1
    return days


from leaves.models import LeaveApplication
from django.utils import timezone
from datetime import timedelta

def apply_leave_deductions(salary_instance):
    """
    Apply salary deductions for unpaid leaves in the pay period.
    Deductions = unpaid_leave_days × (basic_salary / total_days_in_month)
    """

    employee = salary_instance.employee
    pay_start = salary_instance.pay_period_start
    pay_end = salary_instance.pay_period_end

    # Total days in period
    total_days = (pay_end - pay_start).days + 1
    if total_days == 0:
        total_days = 1

    # Daily salary from basic salary
    daily_rate = salary_instance.basic_salary / total_days

    # Fetch unpaid approved leaves in this period
    unpaid_leaves = LeaveApplication.objects.filter(
        employee=employee,
        status="approved",
        leave_type__is_paid=False,
        is_deleted=False,
        end_date__gte=pay_start,
        start_date__lte=pay_end,
    )

    unpaid_days = 0
    for leave in unpaid_leaves:
        # Calculate only the overlapping days
        start = max(leave.start_date, pay_start)
        end = min(leave.end_date, pay_end)
        leave_days = (end - start).days + 1
        unpaid_days += leave_days

    # Final deductions and net salary
    deductions = unpaid_days * daily_rate
    net_salary = salary_instance.basic_salary + salary_instance.allowances - deductions

    # Set values
    salary_instance.deductions = round(deductions, 2)
    salary_instance.net_salary = round(net_salary, 2)

    return salary_instance



# ────────────────────────────────────────────────────────────────────
# Serializers
# ────────────────────────────────────────────────────────────────────
class SalarySerializer(serializers.ModelSerializer):
    employee    = BasicEmployeeSerializer(read_only=True)
    created_by  = CustomUserSerializer(read_only=True)
    modified_by = CustomUserSerializer(read_only=True)
    deleted_by  = CustomUserSerializer(read_only=True)

    # Expose live net salary
    net_salary  = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    deductions  = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Salary
        fields = "__all__"
        read_only_fields = [
            "created_by",
            "modified_by",
            "created_at",
            "updated_at",
            "deleted_by",
            "deleted_at",
            "is_deleted",
            "deductions",
            "net_salary",
        ]


class SalaryCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Admin/HR supplies only: employee, basic_salary, allowances, period dates, payment_date.
    Serializer auto‑fills deductions & net_salary.
    """
    class Meta:
        model = Salary
        fields = [
            "employee",
            "basic_salary",
            "allowances",
            "pay_period_start",
            "pay_period_end",
            "payment_date",
            # read‑only in API:
            "deductions",
            "net_salary",
        ]
        read_only_fields = ["deductions", "net_salary"]

    # ───────── Validation ─────────
    def validate(self, attrs):
        if attrs["pay_period_start"] > attrs["pay_period_end"]:
            raise serializers.ValidationError("Start date cannot be after end date.")
        return attrs

    # ───────── Create / Update ─────────
    def create(self, validated):
        salary = super().create(validated)
        salary = apply_leave_deductions(salary)
        salary.save(update_fields=["deductions", "net_salary"])
        return salary

    def update(self, instance, validated):
        for field, value in validated.items():
            setattr(instance, field, value)
        instance = apply_leave_deductions(instance)
        instance.save(update_fields=[
            "basic_salary", "allowances",
            "pay_period_start", "pay_period_end", "payment_date",
            "deductions", "net_salary"
        ])
        return instance


# ────────────────────────────────────────────────────────────────────
# Aggregation serializers remain unchanged
# ────────────────────────────────────────────────────────────────────
class DepartmentSalarySummarySerializer(serializers.Serializer):
    department           = serializers.CharField()
    employee_count       = serializers.IntegerField()
    total_gross_salary   = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_net_salary     = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_deductions     = serializers.DecimalField(max_digits=12, decimal_places=2)
    average_net_salary   = serializers.DecimalField(max_digits=12, decimal_places=2)
    min_net_salary       = serializers.DecimalField(max_digits=12, decimal_places=2)
    max_net_salary       = serializers.DecimalField(max_digits=12, decimal_places=2)
    last_payment_date    = serializers.DateField()


class DepartmentExpenseSerializer(serializers.Serializer):
    department     = serializers.CharField()
    employee_count = serializers.IntegerField()
    total_expense  = serializers.DecimalField(max_digits=12, decimal_places=2)
