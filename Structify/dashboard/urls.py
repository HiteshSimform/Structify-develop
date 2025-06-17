from django.urls import path
from . import views
from .views import (
    EmployeeListView,
    EmployeeCreateView,
    EmployeeUpdateView,
    EmployeeDeleteView,
)

app_name = "dashboard"

urlpatterns = [
    path("", views.AdminDashboardView.as_view(), name="home"),
    # employee pages
    # path("employees/", views.EmployeeListView.as_view(), name="employees"),
    # path("employees/add/", views.EmployeeCreateView.as_view(), name="employee-add"),
    # path("employees/<int:pk>/edit/", views.EmployeeUpdateView.as_view(), name="employee-edit"),
    # path("employees/delete/<int:pk>/", views.EmployeeDeleteView.as_view(), name="dashboard:employee-delete"),
    path("employees/", EmployeeListView.as_view(), name="employees"),
    path("employees/add/", EmployeeCreateView.as_view(), name="employee-add"),
    path(
        "employees/edit/<int:pk>/", EmployeeUpdateView.as_view(), name="employee-edit"
    ),
    path(
        "employees/delete/<int:pk>/",
        EmployeeDeleteView.as_view(),
        name="employee-delete",
    ),  # Ensure this exists
    # salary pages
    path("salaries/", views.SalaryListView.as_view(), name="salaries"),
    path(
        "salaries/<int:pk>/edit/", views.SalaryUpdateView.as_view(), name="salary-edit"
    ),
    path(
        "salaries/<int:pk>/approve/",
        views.SalaryApproveView.as_view(),
        name="salary-approve",
    ),
    # leaves (AJAX approve / reject)
    path("leaves/", views.LeaveListView.as_view(), name="leaves"),
    path(
        "leaves/<int:pk>/ajax-approve/",
        views.ajax_approve_leave,
        name="leave-ajax-approve",
    ),
    path(
        "leaves/<int:pk>/ajax-reject/",
        views.ajax_reject_leave,
        name="leave-ajax-reject",
    ),
]
