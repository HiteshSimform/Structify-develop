from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import (
    TemplateView,
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.http import JsonResponse, HttpResponseForbidden
from django.urls import reverse_lazy
from django.db.models import Q, Sum, Count, Avg
from django.contrib.auth.mixins import LoginRequiredMixin
from .mixins import HRAdminRequiredMixin
from employees.models import Employees, Department
from employees.forms import EmployeeForm
from salaries.models import Salary
from salaries.forms import SalaryForm
from leaves.models import LeaveApplication
from django.db import models
from django.urls import reverse_lazy


class AdminDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/admin_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["employee_count"] = Employees.objects.filter(is_deleted=False).count()
        context["department_count"] = Department.objects.filter(
            is_deleted=False
        ).count()
        context["total_salary_expense"] = (
            Salary.objects.filter(is_deleted=False).aggregate(
                total=models.Sum("net_salary")
            )["total"]
            or 0
        )
        context["pending_leaves"] = LeaveApplication.objects.filter(
            status="Pending", is_deleted=False
        ).count()
        context["approved_leaves"] = LeaveApplication.objects.filter(
            status="Approved", is_deleted=False
        ).count()
        context["rejected_leaves"] = LeaveApplication.objects.filter(
            status="Rejected", is_deleted=False
        ).count()
        return context


class EmployeeListView(HRAdminRequiredMixin, ListView):
    template_name = "dashboard/employees.html"
    paginate_by = 10
    context_object_name = "employees"

    def get_queryset(self):
        qs = Employees.objects.select_related("user", "department", "designation")
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(
                Q(user__first_name__icontains=q)
                | Q(user__last_name__icontains=q)
                | Q(user__email__icontains=q)
            )
        sort = self.request.GET.get("sort", "user__first_name")
        direction = "" if self.request.GET.get("dir", "asc") == "asc" else "-"
        return qs.order_by(f"{direction}{sort}")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["columns"] = [
            ("user__first_name", "Name"),
            ("user__email", "Email"),
            ("department__name", "Department"),
            ("designation__name", "Designation"),
            ("hire_date", "Hire Date"),
        ]
        return context


class EmployeeCreateView(HRAdminRequiredMixin, CreateView):
    template_name = "dashboard/employee_form.html"
    form_class = EmployeeForm
    success_url = reverse_lazy("dashboard:employees")


class EmployeeUpdateView(HRAdminRequiredMixin, UpdateView):
    template_name = "dashboard/employee_form.html"
    form_class = EmployeeForm
    queryset = Employees.objects.all()
    success_url = reverse_lazy("dashboard:employees")


class SalaryListView(HRAdminRequiredMixin, ListView):
    template_name = "dashboard/salaries.html"
    paginate_by = 10
    context_object_name = "salaries"

    def get_queryset(self):
        qs = Salary.objects.select_related("employee__user", "employee__department")
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(
                Q(employee__user__first_name__icontains=q)
                | Q(employee__user__last_name__icontains=q)
            )
        sort = self.request.GET.get("sort", "payment_date")
        direction = "" if self.request.GET.get("dir", "desc") == "asc" else "-"
        return qs.order_by(f"{direction}{sort}")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["columns"] = [
            ("employee__user__first_name", "Employee"),
            ("net_salary", "Net Salary"),
            ("payment_date", "Payment Date"),
        ]
        return context


class SalaryUpdateView(HRAdminRequiredMixin, UpdateView):
    template_name = "dashboard/salary_form.html"
    form_class = SalaryForm
    queryset = Salary.objects.all()
    success_url = reverse_lazy("dashboard:salaries")


class SalaryApproveView(HRAdminRequiredMixin, TemplateView):
    def get(self, request, pk):
        salary = get_object_or_404(Salary, pk=pk)
        salary.is_approved = True
        salary.save(update_fields=["is_approved"])
        return redirect("dashboard:salaries")


class LeaveListView(HRAdminRequiredMixin, ListView):
    template_name = "dashboard/leaves.html"
    paginate_by = 10
    context_object_name = "leaves"
    queryset = LeaveApplication.objects.select_related("employee__user", "leave_type")


def _leave_permission(user):
    return user.is_superuser or (
        hasattr(user, "employee")
        and user.employee.designation
        and user.employee.designation.name.lower() in ["admin", "hr", "manager"]
    )


def ajax_approve_leave(request, pk):
    if not _leave_permission(request.user):
        return HttpResponseForbidden()
    leave = get_object_or_404(LeaveApplication, pk=pk, status="Pending")
    leave.status = "Approved"
    leave.approver = (
        request.user.employee if hasattr(request.user, "employee") else None
    )
    leave.save(update_fields=["status", "approver"])
    return JsonResponse({"success": True, "new_status": "Approved"})


def ajax_reject_leave(request, pk):
    if not _leave_permission(request.user):
        return HttpResponseForbidden()
    leave = get_object_or_404(LeaveApplication, pk=pk, status="Pending")
    leave.status = "Rejected"
    leave.approver = (
        request.user.employee if hasattr(request.user, "employee") else None
    )
    leave.save(update_fields=["status", "approver"])
    return JsonResponse({"success": True, "new_status": "Rejected"})


class EmployeeDeleteView(HRAdminRequiredMixin, DeleteView):
    template_name = "dashboard/employee_confirm_delete.html"
    queryset = Employees.objects.all()
    success_url = reverse_lazy("dashboard:employees")
