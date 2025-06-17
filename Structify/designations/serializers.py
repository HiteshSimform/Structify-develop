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

# designations/serializers.py

# from rest_framework import serializers
# from .models import Designation


# class DesignationCreateUpdateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Designation
#         fields = ["id", "name", "description"]

#     def validate_name(self, value):
#         value = value.strip()
#         qs = Designation.all_objects.filter(name__iexact=value)
#         if self.instance:
#             qs = qs.exclude(pk=self.instance.pk)
#         if qs.exists():
#             raise serializers.ValidationError("A designation with this name already exists.")
#         return value

#     def validate_description(self, value):
#         return value.strip() if value else value


# class DesignationSerializer(DesignationCreateUpdateSerializer):
#     """Used by staff — includes full audit fields (read-only)"""
#     created_by = serializers.StringRelatedField(read_only=True)
#     modified_by = serializers.StringRelatedField(read_only=True)
#     deleted_by = serializers.StringRelatedField(read_only=True)

#     class Meta(DesignationCreateUpdateSerializer.Meta):
#         fields = DesignationCreateUpdateSerializer.Meta.fields + [
#             "created_by",
#             "modified_by",
#             "deleted_by",
#             "created_at",
#             "updated_at",
#             "is_deleted",
#             "deleted_at",
#         ]
#         read_only_fields = fields


# class PublicDesignationSerializer(serializers.ModelSerializer):
#     """Used by public/non-staff users — only safe fields"""
#     class Meta:
#         model = Designation
#         fields = ["id", "name", "description"]
