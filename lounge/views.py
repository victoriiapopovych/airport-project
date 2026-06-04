from rest_framework import viewsets
from .models import Lounge, LoungeAccess
from .serializers import LoungeDetailSerializer, LoungeListSerializer, LoungeAccessDetailSerializer, LoungeAccessListSerializer, LoungeAccessOperatorUpdateSerializer, LoungeAccessAdminSerializer, LoungeAccessCreateSerializer

from rest_framework.permissions import IsAuthenticated
from lounge.permissions import IsLoungeOperatorOrAdminOrReadOnly, IsLoungeOperatorOrAdmin, CanViewAllLoungeAccesses, CanCreateLoungeAccessForUser, CanCreateOwnLoungeAccess

from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from config.pagination import CustomPagination

import logging
logger = logging.getLogger(__name__)


class LoungeViewSet(viewsets.ModelViewSet):
    queryset = Lounge.objects.all()
    permission_classes = [IsLoungeOperatorOrAdminOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["airport", "is_active", "access_price"]
    search_fields = ["name", "airport__name", "airport__code"]

    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == "list":
            return LoungeListSerializer

        return LoungeDetailSerializer

    def perform_create(self, serializer):
        lounge = serializer.save()

        logger.info(
            "Lounge %s was created by user %s.",
            lounge.id,
            self.request.user.id if self.request.user.is_authenticated else "anonymous",
        )

    def perform_update(self, serializer):
        lounge = serializer.save()

        logger.info(
            "Lounge %s was updated by user %s.",
            lounge.id,
            self.request.user.id if self.request.user.is_authenticated else "anonymous",
        )

    def perform_destroy(self, instance):
        lounge_id = instance.id
        user_id = self.request.user.id if self.request.user.is_authenticated else "anonymous"

        instance.delete()

        logger.warning(
            "Lounge %s was deleted by user %s.",
            lounge_id,
            user_id,
        )


class LoungeAccessViewSet(viewsets.ModelViewSet):
    queryset = LoungeAccess.objects.all()
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["lounge", "status", "access_type", "is_paid", "is_used"]
    search_fields = ["user__email", "user__first_name", "user__last_name", "lounge__name"]

    pagination_class = CustomPagination

    def get_permissions(self):
        if self.action == "create":
            return [CanCreateOwnLoungeAccess()]

        if self.action in ["update", "partial_update", "destroy"]:
            return [IsLoungeOperatorOrAdmin()]

        if self.action == "create_for_user":
            return [CanCreateLoungeAccessForUser()]

        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user

        if CanViewAllLoungeAccesses().has_permission(self.request, self):
            return LoungeAccess.objects.all()

        return LoungeAccess.objects.filter(user=user)

    def get_serializer_class(self):
        serializer_classes = {
            "list": LoungeAccessListSerializer,
            "create": LoungeAccessCreateSerializer,
            "update": LoungeAccessOperatorUpdateSerializer,
            "partial_update": LoungeAccessOperatorUpdateSerializer,
            "create_for_user": LoungeAccessAdminSerializer
        }

        return serializer_classes.get(self.action, LoungeAccessDetailSerializer)
    
    def perform_create(self, serializer):
        lounge_access = serializer.save(user=self.request.user)

        logger.info(
            "Lounge access %s was created by user %s for lounge %s. Access type: %s.",
            lounge_access.id,
            self.request.user.id,
            lounge_access.lounge_id,
            lounge_access.access_type,
        )

    def perform_update(self, serializer):
        old_status = serializer.instance.status
        old_is_paid = serializer.instance.is_paid

        lounge_access = serializer.save()

        logger.info(
            "Lounge access %s was updated by user %s. Status: %s -> %s, is_paid: %s -> %s.",
            lounge_access.id,
            self.request.user.id,
            old_status,
            lounge_access.status,
            old_is_paid,
            lounge_access.is_paid,
        )


    def perform_destroy(self, instance):
        lounge_access_id = instance.id
        user_id = self.request.user.id if self.request.user.is_authenticated else "anonymous"

        instance.delete()

        logger.warning(
            "Lounge access %s was deleted by user %s.",
            lounge_access_id,
            user_id,
        )

    
    @action(detail=False, methods=["post"], url_path="create-for-user")
    def create_for_user(self, request):
        logger.info(
            "User %s started lounge access creation for another user.",
            request.user.id,
        )

        serializer = LoungeAccessAdminSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lounge_access = serializer.save()

        logger.info(
            "Lounge access %s was created by user %s for user %s. Lounge: %s, access type: %s.",
            lounge_access.id,
            request.user.id,
            lounge_access.user_id,
            lounge_access.lounge_id,
            lounge_access.access_type,
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)