from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from users.models import CustomUser

# Create your views here.
from .models import LeaveType, LeaveBalance, LeaveApplication
from .serializers import (
    LeaveTypeSerializer,
    PublicLeaveTypeSerializer,
    LeaveApplicationSerializer,
    LeaveApplicationCreateSerializer,
    LeaveApplicationUpdateStatusSerializer,
    LeaveBalanceSerializer,
    LeaveBalanceCreateUpdateSerializer,
)

from users.permissions import IsMainAdminOrReadOnly
from django.utils import timezone
from .permissions import IsManagerHrOrAdmin
from rest_framework.response import Response
from rest_framework import filters
from .utils import allocate_leave_balances


class LeaveTypeListCreateAPIView(generics.ListCreateAPIView):
    queryset = LeaveType.objects.filter(is_deleted=False)
    serializer_class = LeaveTypeSerializer
    permission_classes = [permissions.IsAuthenticated, IsManagerHrOrAdmin]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, modified_by=self.request.user)


class LeaveTypeRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LeaveType.objects.filter(is_deleted=False)
    serializer_class = LeaveTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "pk"

    def perform_update(self, serializer):
        serializer.save(modified_by=self.request.user)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.deleted_by = self.request.user
        instance.deleted_at = timezone.now()
        instance.save()


class LeaveApplicationListCreateAPIView(generics.ListCreateAPIView):
    queryset = LeaveApplication.objects.filter(is_deleted=False)
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return LeaveApplicationCreateSerializer
        return LeaveApplicationSerializer

    def perform_create(self, serializer):
        serializer.save(
            employee=self.request.user.employee,
            created_by=self.request.user,
            modified_by=self.request.user,
        )


class LeaveApplicationRetriveAPIView(generics.RetrieveAPIView):
    queryset = LeaveApplication.objects.filter(is_deleted=False)
    serializer_class = LeaveApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]


class LeaveApplicationStatusUpdateAPIView(generics.UpdateAPIView):
    queryset = LeaveApplication.objects.filter(is_deleted=False)
    serializer_class = LeaveApplicationUpdateStatusSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        serializer.save(modified_by=self.request.user)


class LeaveBalanceListCreateAPIView(generics.ListCreateAPIView):
    queryset = LeaveBalance.objects.filter(is_deleted=False)
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return LeaveBalanceCreateUpdateSerializer
        return LeaveBalanceSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, modified_by=self.request.user)


class LeaveBalanceRetriveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LeaveBalance.objects.filter(is_deleted=False)
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return LeaveBalanceSerializer
        return LeaveBalanceCreateUpdateSerializer

    def perform_update(self, serializer):
        serializer.save(modified_by=self.request.user)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.deleted_by = self.request.user
        instance.deleted_at = timezone.now()
        instance.save()


class LeaveBalanceReportAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        year = request.query_params.get("year", timezone.now().year)
        emp_id = request.query_params.get("employee_id")

        balances = LeaveBalance.objects.filter(year=year, is_deleted=False)

        if emp_id:
            balances = balances.filter(employee__id=emp_id)

        serializer = LeaveBalanceSerializer(balances, many=True)
        return Response(serializer.data)


class AllocateLeaveBalanceView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, *args, **kwargs):
        employee_id = request.data.get("employee_id")

        try:
            employee = CustomUser.objects.get(id=employee_id)
            allocate_leave_balances(employee=employee, created_by=request.user)
            return Response({"message": "Leave balances allocated successfully."})
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND
            )
