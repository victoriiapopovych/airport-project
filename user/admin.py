from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("email", "first_name", "last_name", "role", "passport_number", "citizenship", "is_verified", "is_staff", "is_active")

    list_filter = ("role", "citizenship", "is_verified", "is_staff", "is_active")

    search_fields = ("email", "first_name", "last_name", "passport_number")

    ordering = ("email",)

    fieldsets = UserAdmin.fieldsets + (
        ("Additional information", {"fields": ("role", "passport_number", "citizenship", "date_of_birth", "phone_number", "is_verified")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "role", "passport_number", "citizenship", "date_of_birth", "phone_number", "is_verified"),
            },
        ),
    )