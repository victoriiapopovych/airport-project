from rest_framework import viewsets
from .models import Lounge, LoungeAccess
from .serializers import LoungeDetailSerializer, LoungeListSerializer, LoungeAccessDetailSerializer, LoungeAccessListSerializer, LoungeAccessOperatorUpdateSerializer, LoungeAccessAdminSerializer, LoungeAccessCreateSerializer

from rest_framework.permissions import IsAuthenticated
from user.models import User
from rest_framework.exceptions import PermissionDenied
from user.permissions import IsLoungeOperatorOrAdminOrReadOnly
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from config.pagination import CustomPagination


class LoungeViewSet(viewsets.ModelViewSet):
    queryset = Lounge.objects.all()
    permission_classes = [IsLoungeOperatorOrAdminOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["airport", "is_active"]
    search_fields = ["name", "airport__name", "airport__code"]

    pagination_class = CustomPagination
    
    def get_serializer_class(self):
        if self.action == "list":
            return LoungeListSerializer
        
        return LoungeDetailSerializer


class LoungeAccessViewSet(viewsets.ModelViewSet):
    queryset = LoungeAccess.objects.all()
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["lounge", "status", "access_type", "is_used"]
    search_fields = ["user__email", "user__first_name", "user__last_name", "lounge__name"]

    pagination_class = CustomPagination

    def is_lounge_operator_or_admin(self, user):
        return (
            user.is_staff
            or user.is_superuser
            or user.role == User.Role.LOUNGE_OPERATOR
        )

    def get_queryset(self):
        user = self.request.user

        if user.is_staff or user.is_superuser or user.role in [
            User.Role.LOUNGE_OPERATOR,
            User.Role.MANAGER,
            User.Role.SUPPORT,
        ]:
            return LoungeAccess.objects.all()

        return LoungeAccess.objects.filter(user=user)

    def get_serializer_class(self):
        if self.action == "list":
            return LoungeAccessListSerializer

        if self.action == "create":
            return LoungeAccessCreateSerializer

        if self.action == "create_for_user":
            return LoungeAccessAdminSerializer

        if self.action in ["update", "partial_update"]:
            return LoungeAccessOperatorUpdateSerializer

        return LoungeAccessDetailSerializer

    def perform_create(self, serializer):
        user = self.request.user

        if user.role in [
            User.Role.SUPPORT,
            User.Role.MANAGER,
            User.Role.LOUNGE_OPERATOR,
        ]:
            raise PermissionDenied("Only passengers can create lounge access requests.")

        if not user.is_verified:
            raise PermissionDenied("Only verified users can create lounge access.")

        serializer.save(user=user)

    def perform_update(self, serializer):
        user = self.request.user

        if not self.is_lounge_operator_or_admin(user):
            raise PermissionDenied("Only lounge operator or admin can update lounge access.")

        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user

        if not self.is_lounge_operator_or_admin(user):
            raise PermissionDenied("Only lounge operator or admin can delete lounge access.")

        instance.delete()

    @action(detail=False, methods=["post"], url_path="create-for-user")
    def create_for_user(self, request):
        user = request.user

        if not (
            user.is_staff
            or user.is_superuser
            or user.role in [
                User.Role.LOUNGE_OPERATOR,
                User.Role.MANAGER,
            ]
        ):
            raise PermissionDenied(
                "Only manager, lounge operator or admin can create lounge access for users."
            )

        serializer = LoungeAccessAdminSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
