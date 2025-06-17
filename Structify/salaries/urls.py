from django.urls import path
from .views import (
    SalaryListCreateAPIView,
    SalaryRetrieveUpdateDestroyAPIView,
    DepartmentSalarySummaryAPIView,
    DepartmentExpenseAPIView,
)

urlpatterns = [
    path("", SalaryListCreateAPIView.as_view(), name="salary-list-create"),
    path(
        "<int:pk>/", SalaryRetrieveUpdateDestroyAPIView.as_view(), name="salary-detail"
    ),
    path(
        "department-summary/",
        DepartmentSalarySummaryAPIView.as_view(),
        name="department-summary",
    ),
    path(
        "department-expense/",
        DepartmentExpenseAPIView.as_view(),
        name="department-expense",
    ),
]
