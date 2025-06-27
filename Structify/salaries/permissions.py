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


class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class IsHrOrSuperAdmin(permissions.BasePermission):
    """
    HR or SuperAdmin required
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        return (
            hasattr(user, "employee")
            and user.employee.designation
            and user.employee.designation.name.lower() == "hr"
        )


class IsSelfOrHrOrSuperAdmin(permissions.BasePermission):
    """
    Only the employee, HR or SuperAdmin can view/modify
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_superuser:
            return True
        if hasattr(user, "employee") and obj == user.employee:
            return True
        if (
            hasattr(user, "employee")
            and user.employee.designation
            and user.employee.designation.name.lower() == "hr"
        ):
            return True
        return False


class IsApproverOrAdmin(permissions.BasePermission):
    """
    Leave can be approved only by HR or Manager or SuperAdmin
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        user = request.user
        if not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        if hasattr(user, "employee") and user.employee.designation:
            role = user.employee.designation.name.lower()
            return role in ["hr", "manager"]

        return False


class IsReadOnly(permissions.BasePermission):
    """
    Allows only SAFE_METHODS (GET, HEAD, OPTIONS)
    """

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsMainAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_superuser
