from django.contrib import admin
from .models import LeaveApplication, LeaveBalance, LeaveType


# Register your models here.
@admin.register(LeaveApplication)
class LeaveApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "leave_type",
        "status",
        "start_date",
        "end_date",
        "approver",
    )
    list_filter = ("status", "leave_type", "employee__designation__name")
    search_fields = ("employee__user__name", "reason")


@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ("employee", "leave_type", "balance_days", "year")
    list_filter = ("year", "leave_type")


admin.site.register(LeaveType)
