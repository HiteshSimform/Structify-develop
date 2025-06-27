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
            "is_paid",
            "created_by",
            "modified_by",
            "created_at",
            "updated_at",
            "is_deleted",
            "deleted_by",
            "deleted_at",
        ]
        read_only_fields = [
            "created_by",
            "modified_by",
            "created_at",
            "updated_at",
            "is_deleted",
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
        fields = ["id", "name", "max_days", "is_paid"]



class LeaveApplicationSerializer(serializers.ModelSerializer):
    employee = BasicEmployeeSerializer(read_only=True)
    leave_type = PublicLeaveTypeSerializer(read_only=True)
    approver = BasicEmployeeSerializer(read_only=True)
    created_by = CustomUserSerializer(read_only=True)
    modified_by = CustomUserSerializer(read_only=True)
    deleted_by = CustomUserSerializer(read_only=True)
    is_paid = serializers.BooleanField(source="leave_type.is_paid", read_only=True)
    total_leave_days = serializers.SerializerMethodField()

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
            "is_paid",
            "total_leave_days",
            "created_by",
            "modified_by",
            "created_at",
            "updated_at",
            "is_deleted",
            "deleted_by",
            "deleted_at",
        ]

    def get_total_leave_days(self, obj):
        return (obj.end_date - obj.start_date).days + 1


class LeaveApplicationCreateSerializer(serializers.ModelSerializer):
    is_paid = serializers.BooleanField(source="leave_type.is_paid", read_only=True)

    class Meta:
        model = LeaveApplication
        fields = [
            "id",
            "leave_type",
            "start_date",
            "end_date",
            "reason",
            "status",
            "is_paid",
        ]
        read_only_fields = ["status", "is_paid"]

    def validate(self, data):
        user = self.context["request"].user
        employee = getattr(user, "employee", None)
        if not employee:
            raise serializers.ValidationError("Employee profile not found.")

        data["employee"] = employee

        start = data.get("start_date")
        end = data.get("end_date")
        leave_type = data.get("leave_type")

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

        total_requested = (end - start).days + 1
        balance = LeaveBalance.objects.filter(
            employee=employee,
            leave_type=leave_type,
            year=timezone.now().year,
            is_deleted=False,
        ).first()

        if not balance:
            raise serializers.ValidationError("No leave balance found for this type.")

        if balance.balance_days < total_requested:
            raise serializers.ValidationError(
                f"Only {balance.balance_days} day(s) available. Not enough balance."
            )

        return data


class LeaveApplicationUpdateStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveApplication
        fields = ["status", "approver"]

    def validate_status(self, value):
        if value not in ["Approved", "Rejected"]:
            raise serializers.ValidationError("Choose Approved or Rejected only.")
        return value


class CompactLeaveApplicationSerializer(serializers.ModelSerializer):
    leave_type = serializers.StringRelatedField()
    is_paid = serializers.BooleanField(source="leave_type.is_paid", read_only=True)
    total_leave_days = serializers.SerializerMethodField()

    class Meta:
        model = LeaveApplication
        fields = [
            "id",
            "start_date",
            "end_date",
            "leave_type",
            "status",
            "is_paid",
            "total_leave_days",
        ]

    def get_total_leave_days(self, obj):
        return (obj.end_date - obj.start_date).days + 1


class LeaveReportSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.user.name", read_only=True)
    leave_type = serializers.CharField(source="leave_type.name", read_only=True)
    is_paid = serializers.BooleanField(source="leave_type.is_paid", read_only=True)
    total_days = serializers.SerializerMethodField()

    class Meta:
        model = LeaveApplication
        fields = [
            "employee_name",
            "leave_type",
            "start_date",
            "end_date",
            "status",
            "is_paid",
            "total_days",
        ]

    def get_total_days(self, obj):
        return (obj.end_date - obj.start_date).days + 1


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


class LeaveBalanceCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveBalance
        fields = ["employee", "leave_type", "balance_days", "year"]

    def validate_balance_days(self, value):
        if value < 0:
            raise serializers.ValidationError("Balance days cannot be negative.")
        return value

    def validate_year(self, value):
        current_year = timezone.now().year
        if value < 2000 or value > current_year + 1:
            raise serializers.ValidationError("Enter a valid year.")
        return value


class LeaveBalanceMinimalSerializer(serializers.ModelSerializer):
    leave_type = serializers.StringRelatedField()

    class Meta:
        model = LeaveBalance
        fields = ["leave_type", "balance_days"]
