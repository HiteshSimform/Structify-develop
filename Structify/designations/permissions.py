# # designations/permissions.py
# from rest_framework import permissions

# class IsHrOrSuperAdmin(permissions.BasePermission):
#     """
#     Full CRUD if:
#       • superuser
#       • HR (designation name == 'hr')
#     Everyone else: read‑only.
#     """

#     def has_permission(self, request, view):
#         user = request.user
#         if not user or not user.is_authenticated:
#             return False

#         if user.is_superuser:
#             return True

#         if hasattr(user, "employee") and user.employee.designation:
#             return user.employee.designation.name.lower() == "hr"

#         # For SAFE methods allow listing
#         return request.method in permissions.SAFE_METHODS
        
# # class IsAdminOrReadOnly(permissions.BasePermission):
# #     """
# #     Only staff users can create/update/delete.
# #     All authenticated users can read.
# #     """
# #     def has_permission(self, request, view):
# #         if request.method in permissions.SAFE_METHODS:
# #             return request.user.is_authenticated
# #         return request.user and request.user.is_staff

# class IsAdminOrReadOnly(permissions.BasePermission):
#     def has_permission(self, request, view):
#         # Allow safe methods for any authenticated user
#         if request.method in permissions.SAFE_METHODS:
#             return request.user and request.user.is_authenticated

#         # Allow write if user is staff or superuser
#         return request.user and (request.user.is_staff or request.user.is_superuser)


from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)
