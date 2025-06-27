from rest_framework import serializers
from .models import Salary
from employees.serializers import BasicEmployeeSerializer
from users.serializers import CustomUserSerializer
from leaves.models import LeaveApplication
from decimal import Decimal


class SalarySerializer(serializers.ModelSerializer):
    """
    Read-only serializer for viewing salary records with full context.
    Includes employee details and deduction from unpaid leaves.
    """

    employee = BasicEmployeeSerializer(read_only=True)
    created_by = CustomUserSerializer(read_only=True)
    modified_by = CustomUserSerializer(read_only=True)
    deleted_by = CustomUserSerializer(read_only=True)
    unpaid_leave_days = serializers.SerializerMethodField()
    unpaid_leave_deduction = serializers.SerializerMethodField()

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
        ]

    def get_unpaid_leave_days(self, obj):
        """
        Returns total unpaid leave days in this pay period.
        """
        return LeaveApplication.objects.filter(
            employee=obj.employee,
            status="approved",
            leave_type__is_paid=False,
            start_date__lte=obj.pay_period_end,
            end_date__gte=obj.pay_period_start,
        ).count()

    def get_unpaid_leave_deduction(self, obj):
        """
        Calculates deduction based on unpaid leave days.
        """
        unpaid_days = self.get_unpaid_leave_days(obj)
        total_days = (obj.pay_period_end - obj.pay_period_start).days + 1 or 30
        daily_rate = obj.basic_salary / Decimal(total_days)
        return round(unpaid_days * daily_rate, 2)


class SalaryCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Used for creating or updating a salary.
    Net salary is automatically calculated.
    """

    class Meta:
        model = Salary
        fields = [
            "employee",
            "basic_salary",
            "allowances",
            "deductions",
            "net_salary",
            "pay_period_start",
            "pay_period_end",
            "payment_date",
        ]

    def validate(self, data):
        """
        Validate salary fields and ensure net_salary matches calculation.
        """
        if data["pay_period_start"] > data["pay_period_end"]:
            raise serializers.ValidationError("Start date cannot be after end date.")

        expected_net = data["basic_salary"] + data["allowances"] - data["deductions"]
        if data["net_salary"] != expected_net:
            raise serializers.ValidationError(
                f"Net salary should be basic + allowances - deductions = {expected_net}"
            )
        return data


class DepartmentSalarySummarySerializer(serializers.Serializer):
    """
    Serializer for department-level salary report analytics.
    """

    department = serializers.CharField()
    employee_count = serializers.IntegerField()
    total_gross_salary = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_net_salary = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_deductions = serializers.DecimalField(max_digits=12, decimal_places=2)
    average_net_salary = serializers.DecimalField(max_digits=12, decimal_places=2)
    min_net_salary = serializers.DecimalField(max_digits=12, decimal_places=2)
    max_net_salary = serializers.DecimalField(max_digits=12, decimal_places=2)
    last_payment_date = serializers.DateField()


class DepartmentExpenseSerializer(serializers.Serializer):
    """
    Serializer for calculating department-wide gross expenses.
    """

    department = serializers.CharField()
    employee_count = serializers.IntegerField()
    total_expense = serializers.DecimalField(max_digits=12, decimal_places=2)
