from rest_framework import viewsets, generics
from .models import User
from .serializers import UserListSerializer, UserDetailSerializer, RegisterSerializer, UserVerificationSerializer

from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .permissions import IsAnonymousOrAdmin
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from config.pagination import CustomPagination


class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [IsAnonymousOrAdmin]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["role", "is_verified", "citizenship"]
    search_fields = ["username", "email", "first_name", "last_name", "passport_number"]

    pagination_class = CustomPagination

    def get_permissions(self):
        if self.action == "create":
            return [IsAdminUser()]

        return [IsAuthenticated()]
    
    def get_queryset(self):
        if (
            self.request.user.is_staff
            or self.request.user.is_superuser
            or self.request.user.role == User.Role.SUPPORT
            or self.request.user.role == User.Role.MANAGER
        ):
            return User.objects.all()

        return User.objects.filter(id=self.request.user.id)
    
    def get_serializer_class(self):
        if self.action == "list":
            return UserListSerializer
        
        if self.action == "retrieve":
            return UserDetailSerializer
        
        return UserDetailSerializer
    
    def perform_destroy(self, instance):
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            raise PermissionDenied("Only admin can delete users.")

        instance.delete()

    def perform_update(self, serializer):
        if self.request.user.is_staff or self.request.user.is_superuser:
            serializer.save()
            return

        if self.request.user.role == User.Role.SUPPORT:
            raise PermissionDenied("Support cannot update users.")

        if serializer.instance != self.request.user:
            raise PermissionDenied("You can update only your own profile.")

        serializer.save()

    @extend_schema(request=UserVerificationSerializer)
    @action(detail=True, methods=["patch"], url_path="verify")
    def verify_user(self, request, pk=None):
        user = self.get_object()

        if not (
            request.user.is_staff
            or request.user.is_superuser
            or request.user.role in [
                User.Role.SUPPORT,
                User.Role.MANAGER,
            ]
        ):
            raise PermissionDenied(
                "Only support, manager or admin can verify users."
            )

        serializer = UserVerificationSerializer(
            user,
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
 