from rest_framework import permissions


class IsAdminOrHR(permissions.BasePermission):
    """
    - Superusers and HRs can view, create, update, delete.
    - Employees can only view their own salaries.
    """

    def has_permission(self, request, view):
        user = request.user
        if user.is_superuser:
            return True

        if hasattr(user, "employee"):
            designation = user.employee.designation.name.lower()
            if designation == "hr":
                return True

            if request.method in permissions.SAFE_METHODS:
                return True

        return False
