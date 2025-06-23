from rest_framework.throttling import SimpleRateThrottle

class EmployeeCreateRateThrottle(SimpleRateThrottle):
    scope = 'employee_create'

    def get_cache_key(self, request, view):
        return f"employee_create_{request.user.id}"