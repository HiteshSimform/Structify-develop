def is_admin_hr_manager(user):
    if user.is_superuser:
        return True
    if hasattr(user, "employee") and user.employee.designation:
        return user.employee.designation.name.lower() in ["hr", "manager"]
    return False
