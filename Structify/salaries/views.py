from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from rest_framework import generics, permissions
from .models import Salary
from .serializers import (
    SalarySerializer,
    SalaryCreateUpdateSerializer,
    DepartmentSalarySummarySerializer,
    DepartmentExpenseSerializer,
)
from django.utils import timezone
from .permissions import IsAdminOrHR
from django.db.models import Sum, Avg, Count, F

from core.permissions import (
    IsAdminOrHR,
    IsMainAdminOrReadOnly,
)
from django.db.models import Sum, Count, F, ExpressionWrapper, DecimalField


class BaseSalaryView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrHR]

    def get_queryset_for_user(self):
        user = self.request.user

        if user.is_superuser or (
            hasattr(user, "employee") and user.employee.designation.name.lower() == "hr"
        ):
            return Salary.objects.filter(is_deleted=False)

        if hasattr(user, "employee"):
            return Salary.objects.filter(employee__user=user, is_deleted=False)

        return Salary.objects.none()


class SalaryListCreateAPIView(BaseSalaryView, generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrHR]
    queryset = Salary.objects.none()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return SalaryCreateUpdateSerializer
        return SalarySerializer

    def get_queryset(self):
        return self.get_queryset_for_user()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, modified_by=self.request.user)


class SalaryRetrieveUpdateDestroyAPIView(
    BaseSalaryView, generics.RetrieveUpdateDestroyAPIView
):
    queryset = Salary.objects.none()

    def get_serializer_class(self):
        if self.request.method == "GET":
            return SalarySerializer
        return SalaryCreateUpdateSerializer

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
    serializer_class = DepartmentSalarySummarySerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrHR]

    def get_queryset(self):
        return (
            Salary.objects.filter(is_deleted=False)
            .values("employee__department__name")
            .annotate(
                department_name=F("employee__department__name"),
                total_net_salary=Sum("net_salary"),
                average_net_salary=Avg("net_salary"),
                employee_count=Count("employee", distinct=True),
            )
            .order_by("department_name")
        )


class DepartmentExpenseAPIView(generics.ListAPIView):
    serializer_class = DepartmentExpenseSerializer
    permission_classes = [permissions.IsAuthenticated, IsMainAdminOrReadOnly]

    def get_queryset(self):
        gross_salary_expr = ExpressionWrapper(
            F("basic_salary") + F("allowances"),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        )
        return (
            Salary.objects.filter(is_deleted=False)
            .values(department=F("employee__department__name"))
            .annotate(
                employee_count=Count("employee", distinct=True),
                total_expense=Sum(gross_salary_expr),
            )
        )
