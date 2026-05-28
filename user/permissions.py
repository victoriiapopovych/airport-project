from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import User


class IsAnonymousOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            not request.user.is_authenticated
            or request.user.is_staff
        )

class CanViewAllUsers(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        return (
            user.is_authenticated
            and (
                user.is_staff
                or user.is_superuser
                or user.role in [
                    User.Role.SUPPORT,
                    User.Role.MANAGER,
                ]
            )
        )


class CanVerifyUsers(BasePermission):
    def has_permission(self, request, view):
        return CanViewAllUsers().has_permission(request, view)


class CanDeleteUsers(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        return (
            user.is_authenticated
            and (
                user.is_staff
                or user.is_superuser
            )
        )
    
class CanUpdateUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user.is_authenticated:
            return False

        if user.is_staff or user.is_superuser:
            return True

        if user.role == User.Role.SUPPORT:
            return False

        return obj == user
    