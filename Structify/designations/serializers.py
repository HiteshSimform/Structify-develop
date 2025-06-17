from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Designation


class DesignationSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    modified_by = serializers.PrimaryKeyRelatedField(read_only=True)
    deleted_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Designation
        fields = [
            "id",
            "name",
            "description",
            "created_by",
            "modified_by",
            "created_at",
            "updated_at",
            "is_deleted",
            "deleted_by",
            "deleted_at",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
            "created_by",
            "modified_by",
            "deleted_by",
            "deleted_at",
        ]


class PublicDesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = ["id", "name", "description"]
