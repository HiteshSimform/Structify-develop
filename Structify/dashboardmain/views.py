from django.shortcuts import render

# Create your views here.
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Count, Avg, F, Q
from employees.models import Employees, Department
from salaries.models import Salary
from leaves.models import LeaveType, LeaveApplication, LeaveBalance
from datetime import date


def is_admin_hr_manager(user):
    if user.is_superuser:
        return True
    if hasattr(user, "employee"):
        designation = user.employee.designation.name.lower()
        return designation in ["hr", "manager"]
    return False


from django.db.models import Sum
from employees.models import Employees
from salaries.models import Salary  # Adjust as per your app name
from leaves.models import LeaveApplication


def dashboard_view(request):
    employees = Employees.objects.all()
    salaries = Salary.objects.all()
    leaves = LeaveApplication.objects.all()

    total_salary = salaries.aggregate(total=Sum("net_salary"))["total"] or 0.00

    context = {
        "employees": employees,
        "salaries": salaries,
        "leaves": leaves,
        "total_salary": total_salary,
    }

    return render(request, "dashboard/index.html", context)


@login_required
@user_passes_test(is_admin_hr_manager)
def home(request):
    departments = Department.objects.all()
    employees = Employees.objects.select_related("user", "department", "designation")
    salaries = Salary.objects.filter(is_deleted=False)

    dept_salary_data = salaries.values("employee__department__name").annotate(
        total_salary=Sum("net_salary"), employee_count=Count("employee", distinct=True)
    )

    context = {
        "departments": departments,
        "employees": employees,
        "salaries": salaries,
        "dept_salary_data": dept_salary_data,
    }
    return render(request, "dashboard/index.html", context)


@login_required
@user_passes_test(is_admin_hr_manager)
def employee_list(request):
    qs = (
        Employees.objects.select_related("user", "department", "designation")
        .filter(is_deleted=False)
        .order_by("department__name", "user__first_name")
    )
    return render(request, "dashboard/employees.html", {"employees": qs})


@login_required
@user_passes_test(is_admin_hr_manager)
def department_list(request):
    qs = Department.objects.filter(is_deleted=False).annotate(
        employee_count=Count("employees", filter=Q(employees__is_deleted=False)),
        total_net_salary=Sum(
            "employees__salaries__net_salary",
            filter=Q(employees__salaries__is_deleted=False),
        ),
    )
    return render(request, "dashboard/departments.html", {"departments": qs})


@login_required
@user_passes_test(is_admin_hr_manager)
def salary_list(request):
    qs = (
        Salary.objects.select_related("employee__user", "employee__department")
        .filter(is_deleted=False)
        .order_by("-payment_date")
    )
    total_month = (
        qs.filter(
            payment_date__month=date.today().month, payment_date__year=date.today().year
        ).aggregate(t=Sum("net_salary"))["t"]
        or 0
    )
    return render(
        request,
        "dashboard/salaries.html",
        {"salaries": qs, "total_month": total_month},
    )


@login_required
@user_passes_test(is_admin_hr_manager)
def leave_overview(request):
    leave_types = LeaveType.objects.filter(is_deleted=False)
    applications = (
        LeaveApplication.objects.select_related(
            "employee__user", "leave_type", "approver__user"
        )
        .filter(is_deleted=False)
        .order_by("-created_at")
    )
    balances = (
        LeaveBalance.objects.select_related("employee__user", "leave_type")
        .filter(is_deleted=False)
        .order_by("employee__user__first_name")
    )
    return render(
        request,
        "dashboard/leaves.html",
        {
            "leave_types": leave_types,
            "applications": applications,
            "balances": balances,
        },
    )
