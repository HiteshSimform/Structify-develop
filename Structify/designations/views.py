from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Designation
from .serializers import DesignationSerializer, PublicDesignationSerializer

from django.shortcuts import get_object_or_404
from django.utils import timezone
from .permissions import IsAdminOrReadOnly
from rest_framework_simplejwt.authentication import JWTAuthentication


class DesignationListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    authentication_classes = [JWTAuthentication]

    def get_serializer_class(self):
        if self.request.user and self.request.user.is_staff:
            return DesignationSerializer
        return PublicDesignationSerializer

    def get(self, request):
        designations = Designation.objects.filter(is_deleted=False)
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(designations, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DesignationSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save(created_by=request.user, modified_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DesignationDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(Designation, pk=pk, is_deleted=False)

    def get_serializer_class(self):
        if self.request.user and self.request.user.is_staff:
            return DesignationSerializer
        return PublicDesignationSerializer

    def get(self, request, pk):
        designation = self.get_object(pk)
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(designation)
        return Response(serializer.data)

    def put(self, request, pk):
        designation = self.get_object(pk)
        serializer = DesignationSerializer(
            designation, data=request.data, partial=False
        )
        if serializer.is_valid():
            serializer.save(modified_by=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        designation = self.get_object(pk)
        serializer = DesignationSerializer(designation, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(modified_by=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        designation = self.get_object(pk)
        designation.is_deleted = True
        designation.deleted_by = request.user
        designation.deleted_at = timezone.now()
        designation.save()
        return Response(
            {"details": "Designation deleted Successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )


# from django.utils import timezone
# from django.shortcuts import get_object_or_404
# from django.db import transaction

# from rest_framework import generics, status, permissions, filters
# from rest_framework.response import Response

# from .models import Designation
# from .serializers import (
#     DesignationSerializer,
#     DesignationCreateUpdateSerializer,
#     PublicDesignationSerializer,
# )
# # from .permissions import IsAdminOrReadOnly, IsHrOrSuperAdmin
# from .permissions import IsAdminOrReadOnly


# # ---------- Helpers -------------------------------------------------- #
# def is_staff(user):
#     return user and (user.is_superuser or user.is_staff)


# # ---------- List + Create ------------------------------------------- #
# class DesignationListCreateAPIView(generics.GenericAPIView):
#     """
#     GET  → paginated list (search, ordering, filter)
#     POST → create single OR bulk (list payload)
#     """
#     permission_classes   = [permissions.IsAuthenticated]
#     queryset             = Designation.objects.all()
#     authentication_classes = []  # handled globally if using JWT

#     # search / ordering
#     filter_backends      = [filters.SearchFilter, filters.OrderingFilter]
#     search_fields        = ["name", "description"]
#     ordering_fields      = ["name", "created_at"]
#     ordering             = ["name"]           # default

#     # ----- serializer selection -----
#     def get_serializer_class(self):
#         if is_staff(self.request.user):
#             # staff can see audit fields on list
#             return DesignationSerializer
#         return PublicDesignationSerializer

#     # ----- list with pagination -----
#     def get(self, request, *args, **kwargs):
#         qs = self.filter_queryset(self.get_queryset())
#         page = self.paginate_queryset(qs)
#         serializer = self.get_serializer(page, many=True)
#         return self.get_paginated_response(serializer.data)

#     # ----- create (single + bulk) -----
#     def post(self, request, *args, **kwargs):
#         payload  = request.data
#         is_bulk  = isinstance(payload, list)
#         serializer_class = DesignationCreateUpdateSerializer

#         serializer = serializer_class(data=payload, many=is_bulk)
#         serializer.is_valid(raise_exception=True)

#         with transaction.atomic():
#             if is_bulk:
#                 instances = serializer.save(
#                     created_by=request.user, modified_by=request.user
#                 )
#                 out = serializer_class(instances, many=True)
#             else:
#                 instance = serializer.save(
#                     created_by=request.user, modified_by=request.user
#                 )
#                 out = serializer_class(instance)

#         code = status.HTTP_201_CREATED
#         return Response(out.data, status=code)


# # ---------- Detail / Update / Delete -------------------------------- #
# class DesignationDetailAPIView(generics.GenericAPIView):
#     """
#     GET    /designations/<pk>/        → retrieve
#     PUT    /designations/<pk>/        → full update
#     PATCH  /designations/<pk>/        → partial update
#     DELETE /designations/<pk>/        → soft delete
#     """
#     permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
#     queryset           = Designation.objects.all()

#     def get_object(self):
#         return get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])

#     def get_serializer_class(self):
#         if self.request.user and self.request.user.is_staff:
#             return DesignationSerializer
#         return PublicDesignationSerializer

#     # ---------- retrieve ----------
#     def get(self, request, *args, **kwargs):
#         obj = self.get_object()
#         serializer = self.get_serializer(obj)
#         return Response(serializer.data)

#     # ---------- full update ----------
#     def put(self, request, *args, **kwargs):
#         obj = self.get_object()
#         serializer = DesignationCreateUpdateSerializer(obj, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save(modified_by=request.user)
#         return Response(serializer.data)

#     # ---------- partial update ----------
#     def patch(self, request, *args, **kwargs):
#         obj = self.get_object()
#         serializer = DesignationCreateUpdateSerializer(
#             obj, data=request.data, partial=True
#         )
#         serializer.is_valid(raise_exception=True)
#         serializer.save(modified_by=request.user)
#         return Response(serializer.data)

#     # ---------- soft delete ----------
#     def delete(self, request, *args, **kwargs):
#         obj = self.get_object()
#         obj.is_deleted  = True
#         obj.deleted_by  = request.user
#         obj.deleted_at  = timezone.now()
#         obj.save()
#         return Response(
#             {"detail": "Designation soft‑deleted successfully."},
#             status=status.HTTP_204_NO_CONTENT,
#         )
