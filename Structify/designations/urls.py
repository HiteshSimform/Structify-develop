from django.urls import path
from .views import DesignationListCreateAPIView, DesignationDetailAPIView

urlpatterns = [
    path(
        "designations/",
        DesignationListCreateAPIView.as_view(),
        name="designation-list-create",
    ),
    path(
        "designations/<int:pk>/",
        DesignationDetailAPIView.as_view(),
        name="designation-detail",
    ),
]
