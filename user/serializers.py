from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    citizenship_name = serializers.CharField(sourse = "citizenship.name", read_only = True)

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
            "is_verified"
        ]


