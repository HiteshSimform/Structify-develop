from django import forms
from employees.models import Employees


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employees
        fields = ["user", "phone_number", "hire_date", "department", "designation"]
        widgets = {
            "hire_date": forms.DateInput(attrs={"type": "date"}),
        }
