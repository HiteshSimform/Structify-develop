from django.shortcuts import render
from rest_framework import generics, status, permissions, filters
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Employees, Department
from .serializers import (
    EmployeeSerializer,
    DepartmentSerializer,
    PublicDepartmentSerializer,
    PublicEmployeeSerializer,
    BasicEmployeeSerializer,
)
from employees.permissions import IsHRManagerSuperAdminOrSelf
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from users.utils import is_hr_manager_or_superadmin
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.db import transaction


class EmployeeListCreateView(generics.ListCreateAPIView):
    """
    List and create employee records.
    - HR, Manager, SuperAdmin: Can list and create any employee record.
    - Employee: Can only create their own record (if HR, Manager, or SuperAdmin).
    """

    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, IsHRManagerSuperAdminOrSelf]

    def get_queryset(self):
        """
        Return a list of employees based on the user's role:
        - HR/Manager/SuperAdmin: All employees.
        - Employee: Only their own record.
        """
        user = self.request.user

        print(f"User: {user}, ID: {user.id}, is_superuser: {user.is_superuser}")

        if is_hr_manager_or_superadmin(user):
            return Employees.objects.all()
        if hasattr(user, "employee"):
            return Employees.objects.filter(user=user)

        print("User is not linked to an employee record.")
        return Employees.objects.none()

    def perform_create(self, serializer):
        """
        Handle employee record creation.
        Only HR, Manager, and SuperAdmin can create records.
        """
        serializer.save(created_by=self.request.user, modified_by=self.request.user)

    def perform_update(self, serializer):
        """
        Handle employee record updates.
        """
        serializer.save(modified_by=self.request.user)


class EmployeeRetriveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or destroy an employee record.
    HR, Manager, SuperAdmin have full access, Employees can only modify their own records.
    """

    queryset = Employees.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, IsHRManagerSuperAdminOrSelf]

    def perform_destroy(self, instance):
        """
        Mark an employee record as deleted (soft delete).
        """
        instance.is_deleted = True
        instance.deleted_by = self.request.user
        instance.deleted_at = timezone.now()
        instance.save()


class EmployeeSearchView(ListAPIView):
    """
    Search for employees by their first name or last name.
    HR, Manager, and SuperAdmin can search all employees.
    Employees can search within their own records.
    """

    serializer_class = BasicEmployeeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Search employees based on query parameters (first or last name).
        """
        user = self.request.user
        query = self.request.query_params.get("q", "")

        if query:
            if is_hr_manager_or_superadmin(user):
                return Employees.objects.filter(
                    Q(user__first_name__icontains=query)
                    | Q(user__last_name__icontains=query),
                    is_deleted=False,
                )

            if hasattr(user, "employee"):
                return Employees.objects.filter(
                    Q(user__first_name__icontains=query)
                    | Q(user__last_name__icontains=query),
                    user=user,
                    is_deleted=False,
                )

        return Employees.objects.none()


# Department


class DepartmentListCreateAPIView(generics.GenericAPIView):
    """
    GET  - paginated list (search / ordering)
    POST - create one or many departments
           (HR / Manager / SuperAdmin only)
    """

    permission_classes = [permissions.IsAuthenticated, IsHRManagerSuperAdminOrSelf]
    queryset = Department.objects.filter(is_deleted=False)

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]  # default

    def get_serializer_class(self):
        if is_hr_manager_or_superadmin(self.request.user):
            return DepartmentSerializer
        return PublicDepartmentSerializer

    def get(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        ser = self.get_serializer(page, many=True)
        return self.get_paginated_response(ser.data)

    def post(self, request, *args, **kwargs):
        data = request.data
        is_bulk = isinstance(data, list)
        ser_class = DepartmentSerializer

        serializer = ser_class(data=data, many=is_bulk)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            if is_bulk:
                instances = serializer.save(
                    created_by=request.user, modified_by=request.user
                )
                out = ser_class(instances, many=True)
            else:
                instance = serializer.save(
                    created_by=request.user, modified_by=request.user
                )
                out = ser_class(instance)

        return Response(out.data, status=status.HTTP_201_CREATED)


class DepartmentDetailAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, IsHRManagerSuperAdminOrSelf]
    queryset = Department.objects.filter(is_deleted=False)

    def get_object(self):
        return get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])

    def get_serializer_class(self):
        if is_hr_manager_or_superadmin(self.request.user):
            return DepartmentSerializer
        return PublicDepartmentSerializer

    def get(self, request, pk, *args, **kwargs):
        obj = self.get_object()
        ser = self.get_serializer(obj)
        return Response(ser.data)

    def put(self, request, pk, *args, **kwargs):
        obj = self.get_object()
        ser = DepartmentSerializer(obj, data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save(modified_by=request.user)
        return Response(ser.data)

    def patch(self, request, pk, *args, **kwargs):
        obj = self.get_object()
        ser = DepartmentSerializer(obj, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save(modified_by=request.user)
        return Response(ser.data)

    def delete(self, request, pk, *args, **kwargs):
        obj = self.get_object()
        obj.is_deleted = True
        obj.deleted_by = request.user
        obj.deleted_at = timezone.now()
        obj.save()
        return Response(
            {"detail": "Department soft‑deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )
