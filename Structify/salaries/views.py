from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum, Avg, Count, F, DecimalField, ExpressionWrapper, Max


from .models import Salary
from .serializers import (
    SalarySerializer,
    SalaryCreateUpdateSerializer,
    DepartmentSalarySummarySerializer,
    DepartmentExpenseSerializer,
)
from .permissions import IsAdminOrHR, IsMainAdminOrReadOnly


class BaseSalaryView(generics.GenericAPIView):
    """
    Abstracts queryset based on the current user's role.
    """

    permission_classes = [permissions.IsAuthenticated, IsAdminOrHR]

    def get_queryset_for_user(self):
        user = self.request.user
        if user.is_superuser or (
            hasattr(user, "employee")
            and user.employee.designation
            and user.employee.designation.name.lower() == "hr"
        ):
            return Salary.objects.filter(is_deleted=False)

        if hasattr(user, "employee"):
            return Salary.objects.filter(employee=user.employee, is_deleted=False)

        return Salary.objects.none()


class SalaryListCreateAPIView(BaseSalaryView, generics.ListCreateAPIView):
    """
    GET: List all salaries (HR/Admin only, employee sees own)
    POST: Create salary
    """

    def get_serializer_class(self):
        return (
            SalaryCreateUpdateSerializer
            if self.request.method == "POST"
            else SalarySerializer
        )

    def get_queryset(self):
        return self.get_queryset_for_user()

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            modified_by=self.request.user,
        )


class SalaryRetrieveUpdateDestroyAPIView(
    BaseSalaryView, generics.RetrieveUpdateDestroyAPIView
):
    """
    GET: Retrieve salary
    PUT/PATCH: Update salary
    DELETE: Soft delete salary
    """

    def get_serializer_class(self):
        return (
            SalaryCreateUpdateSerializer
            if self.request.method in ["PUT", "PATCH"]
            else SalarySerializer
        )

    def get_queryset(self):
        return self.get_queryset_for_user()

    def perform_update(self, serializer):
        serializer.save(modified_by=self.request.user)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.deleted_by = self.request.user
        instance.deleted_at = timezone.now()
        instance.save()


class DepartmentSalarySummaryAPIView(generics.ListAPIView):
    """
    Department-wise salary analytics:
    - Total net/gross/deductions
    - Avg/Min/Max salaries
    """

    serializer_class = DepartmentSalarySummarySerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrHR]

    def get_queryset(self):
        return (
            Salary.objects.filter(is_deleted=False)
            .values(department=F("employee__department__name"))
            .annotate(
                employee_count=Count("employee", distinct=True),
                total_gross_salary=Sum(F("basic_salary") + F("allowances")),
                total_net_salary=Sum("net_salary"),
                total_deductions=Sum("deductions"),
                average_net_salary=Avg("net_salary"),
                min_net_salary=F("net_salary__min"),
                max_net_salary=F("net_salary__max"),
                last_payment_date=Max("payment_date"),
            )
        )


class DepartmentExpenseAPIView(generics.ListAPIView):
    """
    Calculate total gross expenses department-wise.
    """

    serializer_class = DepartmentExpenseSerializer
    permission_classes = [permissions.IsAuthenticated, IsMainAdminOrReadOnly]

    def get_queryset(self):
        gross_salary = ExpressionWrapper(
            F("basic_salary") + F("allowances"),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        )
        return (
            Salary.objects.filter(is_deleted=False)
            .values(department=F("employee__department__name"))
            .annotate(
                employee_count=Count("employee", distinct=True),
                total_expense=Sum(gross_salary),
            )
        )
