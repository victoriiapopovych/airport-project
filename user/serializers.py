from rest_framework import serializers
from .models import User


class UserListSerializer(serializers.ModelSerializer):
    citizenship_name = serializers.CharField(source="citizenship.name", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "role",
            "citizenship_name",
            "is_verified",
        ]


class UserDetailSerializer(serializers.ModelSerializer):
    citizenship_name = serializers.CharField(source="citizenship.name", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",

            # AbstractUser fields
            "username",
            "first_name",
            "last_name",
            "email",

            # CustomUser fields
            "role",
            "passport_number",
            "citizenship",
            "citizenship_name",
            "date_of_birth",
            "phone_number",
            "is_verified",
        ]
