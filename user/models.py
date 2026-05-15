from django.db import models
from django.contrib.auth.models import AbstractUser
from location.models import Country

# Create your models here.
class User(AbstractUser):
    class Role(models.TextChoices):
        PASSENGER = "passenger", "Passenger"
        SUPPORT = "support", "Support"
        MANAGER = "manager", "Manager"
        

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PASSENGER)
    passport_number = models.CharField(max_length=20, unique=True)
    citizenship = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name="users")
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        full_name = self.get_full_name()

        if full_name:
            return f"{full_name} ({self.role})"

        return f"{self.username} ({self.role})"