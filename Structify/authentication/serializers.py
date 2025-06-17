from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth import authenticate
from users.models import CustomUser
import re
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            raise ValidationError("Email and Password are required")

        user = authenticate(email=email, password=password)
        if not user:
            raise ValidationError("Invalid user or password")
        user.last_login = timezone.now()
        user.save()

        refresh = RefreshToken.for_user(user)

        return {
            "user": {"id": user.id, "email": user.email},
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "message": "Login Successfull",
        }
