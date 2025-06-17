from django import forms
from salaries.models import Salary


class SalaryForm(forms.ModelForm):
    class Meta:
        model = Salary
        fields = [
            "basic_salary",
            "allowances",
            "deductions",
            "pay_period_start",
            "pay_period_end",
            "payment_date",
        ]
        widgets = {
            "pay_period_start": forms.DateInput(attrs={"type": "date"}),
            "pay_period_end": forms.DateInput(attrs={"type": "date"}),
            "payment_date": forms.DateInput(attrs={"type": "date"}),
        }
