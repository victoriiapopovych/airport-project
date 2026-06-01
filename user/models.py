from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from location.models import Country


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required.")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)
    
# Create your models here.
class User(AbstractUser):
    class Role(models.TextChoices):
        PASSENGER = "passenger", "Passenger"
        SUPPORT = "support", "Support"
        MANAGER = "manager", "Manager"
        LOUNGE_OPERATOR = "lounge_operator", "Lounge Operator"

    username = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

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

        return f"{self.email} ({self.role})"