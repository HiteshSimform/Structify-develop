from django.utils import timezone
from rest_framework import generics, permissions, status, filters as drf_filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import LeaveType, LeaveBalance, LeaveApplication
from .serializers import (
    LeaveTypeSerializer,
    LeaveApplicationSerializer,
    LeaveApplicationCreateSerializer,
    LeaveApplicationUpdateStatusSerializer,
    LeaveBalanceSerializer,
    LeaveBalanceCreateUpdateSerializer,
    LeaveReportSerializer,
)
from .permissions import IsManagerHrOrAdmin
from .utils import allocate_leave_balances
from users.models import CustomUser

from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class LeaveTypeListCreateAPIView(generics.ListCreateAPIView):
    queryset = LeaveType.objects.filter(is_deleted=False)
    serializer_class = LeaveTypeSerializer
    permission_classes = [permissions.IsAuthenticated, IsManagerHrOrAdmin]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, modified_by=self.request.user)


class LeaveTypeRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LeaveType.objects.filter(is_deleted=False)
    serializer_class = LeaveTypeSerializer
    permission_classes = [permissions.IsAuthenticated, IsManagerHrOrAdmin]
    lookup_field = "pk"

    def perform_update(self, serializer):
        serializer.save(modified_by=self.request.user)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.deleted_by = self.request.user
        instance.deleted_at = timezone.now()
        instance.save()


class LeaveApplicationListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        drf_filters.SearchFilter,
        drf_filters.OrderingFilter,
    ]
    filterset_fields = ["leave_type__id", "status", "employee__id"]
    search_fields = ["reason"]
    ordering_fields = ["start_date", "end_date", "status"]
    ordering = ["-start_date"]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or (
            hasattr(user, "employee")
            and user.employee.designation.name.lower() in ["hr", "manager"]
        ):
            return LeaveApplication.objects.filter(is_deleted=False)
        return LeaveApplication.objects.filter(employee=user.employee, is_deleted=False)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return LeaveApplicationCreateSerializer
        return LeaveApplicationSerializer

    def perform_create(self, serializer):
        employee = self.request.user.employee
        serializer.save(
            employee=employee,
            created_by=self.request.user,
            modified_by=self.request.user,
        )


class LeaveApplicationRetriveAPIView(generics.RetrieveAPIView):
    queryset = LeaveApplication.objects.filter(is_deleted=False)
    serializer_class = LeaveApplicationSerializer
    permission_classes = [permissions.IsAuthenticated, IsManagerHrOrAdmin]


class LeaveApplicationStatusUpdateAPIView(generics.UpdateAPIView):
    queryset = LeaveApplication.objects.filter(is_deleted=False)
    serializer_class = LeaveApplicationUpdateStatusSerializer
    permission_classes = [permissions.IsAuthenticated, IsManagerHrOrAdmin]

    def perform_update(self, serializer):
        instance = serializer.save(modified_by=self.request.user)

        if instance.status == "Approved":
            total_days = (instance.end_date - instance.start_date).days + 1
            balance = LeaveBalance.objects.filter(
                employee=instance.employee,
                leave_type=instance.leave_type,
                year=timezone.now().year,
                is_deleted=False,
            ).first()
            if balance:
                balance.balance_days = max(0, balance.balance_days - total_days)
                balance.modified_by = self.request.user
                balance.save()


class LeaveBalanceListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, drf_filters.OrderingFilter]
    filterset_fields = ["employee__id", "leave_type__id", "year"]
    ordering_fields = ["year", "balance_days"]
    ordering = ["-year"]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or (
            hasattr(user, "employee")
            and user.employee.designation.name.lower() in ["hr", "manager"]
        ):
            return LeaveBalance.objects.filter(is_deleted=False)
        return LeaveBalance.objects.filter(employee=user.employee, is_deleted=False)

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


class LeaveReportListAPIView(generics.ListAPIView):
    serializer_class = LeaveReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, drf_filters.OrderingFilter]
    filterset_fields = ["employee__id", "status", "leave_type__id"]
    ordering_fields = ["start_date", "end_date"]
    ordering = ["-start_date"]

    def get_queryset(self):
        year = self.request.query_params.get("year", timezone.now().year)
        return LeaveApplication.objects.filter(
            start_date__year=year,
            is_deleted=False,
        )


class AllocateLeaveBalanceView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        employee_id = request.data.get("employee_id")
        try:
            employee = CustomUser.objects.get(id=employee_id)
            allocate_leave_balances(employee=employee, created_by=request.user)
            return Response({"message": "Leave balances allocated successfully."})
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND
            )
