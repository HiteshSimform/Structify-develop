from django.urls import path
from .views import (
    LeaveTypeListCreateAPIView,
    LeaveTypeRetrieveUpdateDestroyAPIView,
    LeaveApplicationListCreateAPIView,
    LeaveApplicationRetriveAPIView,
    LeaveApplicationStatusUpdateAPIView,
    LeaveBalanceListCreateAPIView,
    LeaveBalanceRetriveUpdateDestroyAPIView,
    LeaveBalanceReportAPIView,
    AllocateLeaveBalanceView,
)

urlpatterns = [
    # LeaveType
    path("types/", LeaveTypeListCreateAPIView.as_view(), name="leave-type-list-create"),
    path(
        "types/<int:pk>/",
        LeaveTypeRetrieveUpdateDestroyAPIView.as_view(),
        name="leave-type-detail",
    ),
    # LeaveApplication
    path(
        "applications/",
        LeaveApplicationListCreateAPIView.as_view(),
        name="leave-app-list-create",
    ),
    path(
        "applications/<int:pk>/",
        LeaveApplicationRetriveAPIView.as_view(),
        name="leave-app-detail",
    ),
    path(
        "applications/<int:pk>/status/",
        LeaveApplicationStatusUpdateAPIView.as_view(),
        name="leave-app-status-update",
    ),
    # LeaveBalance
    path(
        "balances/",
        LeaveBalanceListCreateAPIView.as_view(),
        name="leave-balance-list-create",
    ),
    path(
        "balances/<int:pk>/",
        LeaveBalanceRetriveUpdateDestroyAPIView.as_view(),
        name="leave-balance-detail",
    ),
    path(
        "report/leave-balance/",
        LeaveBalanceReportAPIView.as_view(),
        name="leave-balance-report",
    ),
    path(
        "allocate-leaves/", AllocateLeaveBalanceView.as_view(), name="allocate-leaves"
    ),
]
