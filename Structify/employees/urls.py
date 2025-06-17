from django.urls import path
from .views import (
    EmployeeListCreateView,
    EmployeeRetriveUpdateDestroyView,
    EmployeeSearchView,
)

urlpatterns = [
    path("employees/", EmployeeListCreateView.as_view(), name="employee-list-create"),
    path(
        "employees/<int:pk>/",
        EmployeeRetriveUpdateDestroyView.as_view(),
        name="employee-detail",
    ),
    path("search/", EmployeeSearchView.as_view(), name="employee-search"),
]
