from django.contrib import admin
from .models import Salary


# Register your models here.
@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin):
    """
    Admin configuration for Salary model.
    Provides list display, filtering, and search options.
    """

    list_display = (
        "employee",
        "basic_salary",
        "allowances",
        "deductions",
        "net_salary",
        "pay_period_start",
        "pay_period_end",
        "payment_date",
        "is_deleted",
    )
    list_filter = (
        "payment_date",
        "employee__department__name",
        "employee__designation__name",
        "is_deleted",
    )
    search_fields = (
        "employee__user__name",
        "employee__user__email",
        "employee__department__name",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "created_by",
        "modified_by",
        "deleted_by",
        "deleted_at",
    )
    ordering = ("-payment_date",)

    def get_queryset(self, request):
        """
        Custom queryset to exclude deleted salaries by default in admin panel.
        """
        qs = super().get_queryset(request)
        return qs.filter(is_deleted=False)
