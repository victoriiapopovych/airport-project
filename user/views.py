from rest_framework import viewsets, generics
from .models import User
from .serializers import UserListSerializer, UserDetailSerializer, RegisterSerializer, UserVerificationSerializer

from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .permissions import IsAnonymousOrAdmin, CanDeleteUsers, CanVerifyUsers, CanViewAllUsers, CanUpdateUser

from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from config.pagination import CustomPagination

import logging
logger = logging.getLogger(__name__)


class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [IsAnonymousOrAdmin]

    def perform_create(self, serializer):
        user = serializer.save()

        logger.info(
            "User %s registered successfully with role %s.",
            user.id,
            user.role,
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["role", "is_verified", "citizenship"]
    search_fields = ["email", "first_name", "last_name", "passport_number"]

    pagination_class = CustomPagination

    def get_permissions(self):
        if self.action == "create":
            return [IsAdminUser()]
        
        if self.action in ["update", "partial_update"]:
            return [CanUpdateUser()]

        if self.action == "destroy":
            return [CanDeleteUsers()]

        if self.action == "verify_user":
            return [CanVerifyUsers()]

        return [IsAuthenticated()]
    
    def get_queryset(self):
        if CanViewAllUsers().has_permission(self.request, self):
            return User.objects.all()

        return User.objects.filter(id=self.request.user.id)
    
    def get_serializer_class(self):
        if self.action == "list":
            return UserListSerializer
    
        return UserDetailSerializer
    
    def perform_create(self, serializer):
        user = serializer.save()

        logger.info(
            "User %s was created by admin user %s with role %s.",
            user.id,
            self.request.user.id if self.request.user.is_authenticated else "anonymous",
            user.role,
        )


    def perform_update(self, serializer):
        old_is_verified = serializer.instance.is_verified
        old_role = serializer.instance.role

        user = serializer.save()

        logger.info(
            "User %s was updated by user %s. Role: %s -> %s, is_verified: %s -> %s.",
            user.id,
            self.request.user.id if self.request.user.is_authenticated else "anonymous",
            old_role,
            user.role,
            old_is_verified,
            user.is_verified,
        )


    def perform_destroy(self, instance):
        user_id = instance.id
        deleted_by = self.request.user.id if self.request.user.is_authenticated else "anonymous"

        instance.delete()

        logger.warning(
            "User %s was deleted by user %s.",
            user_id,
            deleted_by,
        )

    @extend_schema(request=UserVerificationSerializer)
    @action(detail=True, methods=["patch"], url_path="verify")
    def verify_user(self, request, pk=None):
        user = self.get_object()
        old_is_verified = user.is_verified

        serializer = UserVerificationSerializer(user, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        logger.info(
            "User %s verification status was changed by user %s: %s -> %s.",
            user.id,
            request.user.id,
            old_is_verified,
            serializer.instance.is_verified,
        )

        return Response(serializer.data)