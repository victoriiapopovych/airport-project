from rest_framework.permissions import BasePermission
from user.models import User


class IsLoungeOperatorOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (
                request.user.is_staff
                or request.user.is_superuser
                or request.user.role == User.Role.LOUNGE_OPERATOR
            )
        )


class CanViewAllLoungeAccesses(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (
                request.user.is_staff
                or request.user.is_superuser
                or request.user.role in [
                    User.Role.LOUNGE_OPERATOR,
                    User.Role.MANAGER,
                    User.Role.SUPPORT,
                ]
            )
        )


class CanCreateLoungeAccessForUser(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (
                request.user.is_staff
                or request.user.is_superuser
                or request.user.role in [
                    User.Role.LOUNGE_OPERATOR,
                    User.Role.MANAGER,
                ]
            )
        )
    

class CanCreateOwnLoungeAccess(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_verified
            and not CanViewAllLoungeAccesses().has_permission(request, view)
        )