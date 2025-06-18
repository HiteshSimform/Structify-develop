from rest_framework import serializers
from .models import Salary
from employees.serializers import PublicDepartmentSerializer
from users.serializers import CustomUserSerializer


class SalarySerializer(serializers.ModelSerializer):
    employee = PublicDepartmentSerializer(read_only=True)
    created_by = CustomUserSerializer(read_only=True)
    modified_by = CustomUserSerializer(read_only=True)
    deleted_by = CustomUserSerializer(read_only=True)

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


class SalaryCreateUpdateSerializer(serializers.ModelSerializer):
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
            if data["pay_period_start"] > data["pay_period_end"]:
                raise serializers.ValidationError(
                    "start date can not be after end date."
                )
            if (
                data["net_salary"]
                != data["basic_salary"] + data["allowances"] - data["deductions"]
            ):
                raise serializers.ValidationError(
                    "Net salary does not match the expected calculation: basic + allowances - deductions."
                )
            return data


class DepartmentSalarySummarySerializer(serializers.Serializer):
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
    department = serializers.CharField()
    employee_count = serializers.IntegerField()
    total_expense = serializers.DecimalField(max_digits=12, decimal_places=2)
