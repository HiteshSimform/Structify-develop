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
