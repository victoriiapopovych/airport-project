from rest_framework import serializers
from .models import User


class UserListSerializer(serializers.ModelSerializer):
    citizenship_name = serializers.CharField(source="citizenship.name", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
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
            "email",
            "password",
            "first_name",
            "last_name",
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
        password = validated_data.pop("password", None)

        return User.objects.create_user(
            password=password,
            **validated_data
        )

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
        validated_data["role"] = User.Role.PASSENGER
        validated_data["is_verified"] = False

        return User.objects.create_user(**validated_data)
    
 
class UserVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["is_verified"]
