# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status, permissions
# from django.shortcuts import get_object_or_404
# from django.utils import timezone

# from .models import Designation
# from .serializers import DesignationSerializer, PublicDesignationSerializer
# from .permissions import IsAdminUser, IsAuthenticatedOrReadOnlyForPublic

# class DesignationListCreateAPIView(APIView):
#     permission_classes = [IsAuthenticatedOrReadOnlyForPublic]

#     def get(self, request):
#         designations = Designation.objects.filter(is_deleted=False)

#         # Now use permissions, no need for if-else here
#         if request.user.is_staff:
#             serializer = DesignationSerializer(designations, many=True)
#         else:
#             serializer = PublicDesignationSerializer(designations, many=True)
#         return Response(serializer.data)

#     def post(self, request):
#         # Permission is already handled at the class level
#         serializer = DesignationSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(created_by=request.user, modified_by=request.user)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class DesignationDetailAPIView(APIView):
#     permission_classes = [permissions.IsAuthenticated, IsAdminUser]

#     def get_object(self, pk):
#         return get_object_or_404(Designation, pk=pk, is_deleted=False)

#     def get(self, request, pk):
#         designation = self.get_object(pk)

#         # You still want different serializers for public vs admin users:
#         if request.user.is_staff:
#             serializer = DesignationSerializer(designation)
#         else:
#             serializer = PublicDesignationSerializer(designation)
#         return Response(serializer.data)

#     def put(self, request, pk):
#         designation = self.get_object(pk)
#         serializer = DesignationSerializer(designation, data=request.data, partial=False)
#         if serializer.is_valid():
#             serializer.save(modified_by=request.user)
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def patch(self, request, pk):
#         designation = self.get_object(pk)
#         serializer = DesignationSerializer(designation, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save(modified_by=request.user)
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, pk):
#         designation = self.get_object(pk)
#         designation.is_deleted = True
#         designation.deleted_by = request.user
#         designation.deleted_at = timezone.now()
#         designation.save()
#         return Response({"details": "Designation deleted Successfully"}, status=status.HTTP_204_NO_CONTENT)


# # permissions.py
# from rest_framework import permissions

# class IsAdminUser(permissions.BasePermission):
#     """
#     Allows access only to admin users (staff).
#     """
#     def has_permission(self, request, view):
#         return bool(request.user and request.user.is_staff)


# class IsAuthenticatedOrReadOnlyForPublic(permissions.BasePermission):
#     """
#     Allow any user to GET (read) public info,
#     but only authenticated users (admins) can access full info or modify.
#     """

#     def has_permission(self, request, view):
#         # Safe methods (GET, HEAD, OPTIONS) are allowed for everyone
#         if request.method in permissions.SAFE_METHODS:
#             return True

#         # Write methods require admin
#         return bool(request.user and request.user.is_staff)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Designation
from .serializers import DesignationSerializer, PublicDesignationSerializer
from .permissions import IsAdminOrReadOnly


class DesignationListCreateAPIView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        # Return serializer based on user
        if self.request.user and self.request.user.is_staff:
            return DesignationSerializer
        return PublicDesignationSerializer

    def get(self, request):
        designations = Designation.objects.filter(is_deleted=False)
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(designations, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DesignationSerializer(
            data=request.data
        )  # Post only allowed for admin by permission
        if serializer.is_valid():
            serializer.save(created_by=request.user, modified_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DesignationDetailAPIView(APIView):
    permission_classes = [IsAdminOrReadOnly]

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
        )  # Only admin can call (permission)
        if serializer.is_valid():
            serializer.save(modified_by=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        designation = self.get_object(pk)
        serializer = DesignationSerializer(
            designation, data=request.data, partial=True
        )  # Only admin can call (permission)
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


# permissions.py

from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allow full access only to admins (staff), read-only to others.
    """

    def has_permission(self, request, view):
        # Allow GET, HEAD, OPTIONS for everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        # Otherwise, only admins
        return bool(request.user and request.user.is_staff)
