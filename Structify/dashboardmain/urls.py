from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.home, name="home"),
    path("employees/", views.employee_list, name="employees"),
    path("departments/", views.department_list, name="departments"),
    path("salaries/", views.salary_list, name="salaries"),
    path("leaves/", views.leave_overview, name="leaves"),
]
