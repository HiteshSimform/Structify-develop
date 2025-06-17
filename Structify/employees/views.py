from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.generics import ListAPIView

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Employees, Department
from .serializers import (
    EmployeeSerializer,
    DepartmentSerializer,
    PublicDepartmentSerializer,
    PublicEmployeeSerializer,
)
from employees.permissions import IsHRManagerSuperAdminOrSelf
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from users.utils import is_hr_manager_or_superadmin
from django.db.models import Q


class EmployeeListCreateView(generics.ListCreateAPIView):
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, IsHRManagerSuperAdminOrSelf]

    def get_queryset(self):
        user = self.request.user
        print(f"User: {user}, ID: {user.id}, is_superuser: {user.is_superuser}")

        if is_hr_manager_or_superadmin(user):
            return Employees.objects.all()

        if hasattr(user, "employee"):
            return Employees.objects.filter(user=user)

        print("User is not linked to an employee record.")
        return Employees.objects.none()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, modified_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(modified_by=self.request.user)


class EmployeeRetriveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Employees.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, IsHRManagerSuperAdminOrSelf]

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.deleted_by = self.request.user
        instance.deleted_at = timezone.now()
        instance.save()


class EmployeeSearchView(ListAPIView):
    serializer_class = PublicEmployeeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        query = self.request.query_params.get("q", "")
        if query:
            return Employees.objects.filter(
                Q(user__first_name__icontains=query)
                | Q(user__last_name__icontains=query),
                is_deleted=False,
            )
        return Employees.objects.none()
