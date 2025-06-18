from django.urls import path
from .views import (
    EmployeeListCreateView,
    EmployeeRetriveUpdateDestroyView,
    EmployeeSearchView,
    DepartmentListCreateAPIView,
    DepartmentDetailAPIView,
)

urlpatterns = [
    path("employees/", EmployeeListCreateView.as_view(), name="employee-list-create"),
    path(
        "employees/<int:pk>/",
        EmployeeRetriveUpdateDestroyView.as_view(),
        name="employee-detail",
    ),
    path("search/", EmployeeSearchView.as_view(), name="employee-search"),
    path(
        "departments/",
        DepartmentListCreateAPIView.as_view(),
        name="department-list-create",
    ),
    path(
        "departments/<int:pk>/",
        DepartmentDetailAPIView.as_view(),
        name="department-detail",
    ),
]
