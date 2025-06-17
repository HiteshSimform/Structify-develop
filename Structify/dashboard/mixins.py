from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class HRAdminRequiredMixin(UserPassesTestMixin):
    """
    Allows access only to:
    - Superusers
    - Users whose related employee.designation is 'hr' or 'admin'
    """

    def test_func(self):
        user = self.request.user

        if not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        if hasattr(user, "employee") and user.employee.designation:
            designation = user.employee.designation.name.lower()
            return designation in ["hr", "admin"]

        return False

    def handle_no_permission(self):
        raise PermissionDenied("You do not have permission to access this page.")
