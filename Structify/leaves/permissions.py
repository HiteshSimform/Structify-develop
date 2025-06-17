from rest_framework import permissions


class IsManagerHrOrAdmin(permissions.BasePermission):
    """
    Allows access only to users who are either:
    - Superuser (mainadmin)
    - Manager
    - HR
    """

    def has_permission(self, request, view):
        user = request.user

        # Allow if superuser
        if user.is_superuser:
            return True

        # Allow if role is HR or Manager
        if hasattr(user, "employee") and user.employee.designation:
            role = user.employee.designation.name.lower()
            return role in ["hr", "manager"]

        return False
