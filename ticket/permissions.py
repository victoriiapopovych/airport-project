from rest_framework.permissions import BasePermission
from user.models import User


class CanViewAllBookings(BasePermission):
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


class CanCreateBooking(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        return (
            user.is_authenticated
            and user.is_verified
            and user.role not in [
                User.Role.SUPPORT,
                User.Role.MANAGER,
            ]
        )


class CanCancelBooking(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user.is_authenticated:
            return False

        if CanViewAllBookings().has_permission(request, view):
            return True

        return obj.user == user