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
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "id",

            # AbstractUser fields
            "username",
            "first_name",
            "last_name",
            "email",
            "password",

            # CustomUser fields
            "role",
            "passport_number",
            "citizenship",
            "citizenship_name",
            "date_of_birth",
            "phone_number",
            "is_verified",
        ]
        read_only_fields = ["id", "role", "is_verified"]
 
    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance
 

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "passport_number",
            "citizenship",
            "date_of_birth",
            "phone_number",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = User(**validated_data)
        user.role = User.Role.PASSENGER
        user.is_verified = False
        user.set_password(password)
        user.save()

        return user
 
class UserVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["is_verified"]
