from rest_framework import serializers
from .models import LeaveType, LeaveApplication, LeaveBalance
from employees.serializers import BasicEmployeeSerializer
from users.serializers import CustomUserSerializer
from django.utils import timezone


class LeaveTypeSerializer(serializers.ModelSerializer):
    created_by = CustomUserSerializer(read_only=True)
    modified_by = CustomUserSerializer(read_only=True)
    deleted_by = CustomUserSerializer(read_only=True)

    class Meta:
        model = LeaveType
        fields = [
            "id",
            "name",
            "description",
            "max_days",
            "created_by",
            "modified_by",
            "created_at",
            "updated_at",
            "is_deleted",
            "deleted_by",
            "deleted_at",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
            "created_by",
            "modified_by",
            "deleted_by",
            "deleted_at",
        ]

    def validate_max_days(self, value):
        if value <= 0:
            raise serializers.ValidationError("Max days must be greater than zero.")
        return value


class PublicLeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = ["id", "name", "max_days"]


class LeaveApplicationSerializer(serializers.ModelSerializer):
    employee = BasicEmployeeSerializer(read_only=True)
    leave_type = PublicLeaveTypeSerializer(read_only=True)
    approver = BasicEmployeeSerializer(read_only=True)
    created_by = CustomUserSerializer(read_only=True)
    modified_by = CustomUserSerializer(read_only=True)
    deleted_by = CustomUserSerializer(read_only=True)

    class Meta:
        model = LeaveApplication
        fields = [
            "id",
            "employee",
            "leave_type",
            "start_date",
            "end_date",
            "reason",
            "status",
            "approver",
            "created_by",
            "modified_by",
            "created_at",
            "updated_at",
            "is_deleted",
            "deleted_by",
            "deleted_at",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
            "status",
            "approver",
            "created_by",
            "modified_by",
            "deleted_by",
            "deleted_at",
        ]


class LeaveApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveApplication
        fields = [
            "id",
            "employee",
            "leave_type",
            "start_date",
            "end_date",
            "reason",
        ]

    def validate(self, data):
        employee = self.context["request"].user.employee
        start = data["start_date"]
        end = data["end_date"]

        if start > end:
            raise serializers.ValidationError("Start date cannot be after end date.")

        if start < timezone.now().date():
            raise serializers.ValidationError("Leave cannot start in the past.")

        overlapping = LeaveApplication.objects.filter(
            employee=employee,
            start_date__lte=end,
            end_date__gte=start,
            is_deleted=False,
        ).exists()

        if overlapping:
            raise serializers.ValidationError("An overlapping leave already exists.")

        return data


class LeaveApplicationUpdateStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveApplication
        fields = ["status", "approver"]

    def validate_status(self, value):
        if value not in ["Approved", "Rejected"]:
            raise serializers.ValidationError(
                "Invalid status. Choose Approved or Rejected."
            )
        return value


class LeaveBalanceSerializer(serializers.ModelSerializer):
    employee = BasicEmployeeSerializer(read_only=True)
    leave_type = PublicLeaveTypeSerializer(read_only=True)
    created_by = CustomUserSerializer(read_only=True)
    modified_by = CustomUserSerializer(read_only=True)
    deleted_by = CustomUserSerializer(read_only=True)

    class Meta:
        model = LeaveBalance
        fields = [
            "id",
            "employee",
            "leave_type",
            "balance_days",
            "year",
            "created_by",
            "modified_by",
            "created_at",
            "updated_at",
            "is_deleted",
            "deleted_by",
            "deleted_at",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
            "created_by",
            "modified_by",
            "deleted_by",
            "deleted_at",
        ]


class LeaveBalanceCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveBalance
        fields = [
            "employee",
            "leave_type",
            "balance_days",
            "year",
        ]

    def validate_balance_days(self, value):
        if value < 0:
            raise serializers.ValidationError("Balance days cannot be negative.")
        return value

    def validate_year(self, value):
        if value < 2000 or value > timezone.now().year + 1:
            raise serializers.ValidationError("Enter a valid year.")
        return value
