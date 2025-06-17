from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsHRManagerSuperAdminOrSelf(BasePermission):
    """
    Permissions:
    - HR, Manager, SuperAdmin: full access to all employees.
    - Employee: access limited to own employee record.
    - Create only by HR, Manager, SuperAdmin.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True

        if request.method == "POST":
            return self.is_hr_manager_or_superadmin(user)

        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        if self.is_hr_manager_or_superadmin(user):
            return True

        if hasattr(user, "employee") and obj == user.employee:
            return True

        return False

    def is_hr_manager_or_superadmin(self, user):
        if user.is_superuser:
            return True

        if not hasattr(user, "employee"):
            return False

        # designation = getattr(user.employee.designation, None)
        # if not designation:
        #     return False
        # role_name = designation.name.strip().lower()
        designation = user.employee.designation
        if not designation:
            return False
        role_name = designation.name.strip().lower()

        return role_name in ["hr", "manager"]
