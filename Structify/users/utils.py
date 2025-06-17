def is_hr_manager_or_superadmin(user):
    if user.is_superuser:
        return True

    if hasattr(user, "employee") and user.employee.designation:
        role = user.employee.designation.name.strip().lower()
        return role in ["hr", "manager"]

    return False
