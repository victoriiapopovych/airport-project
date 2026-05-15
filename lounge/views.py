from rest_framework import viewsets
from .models import Lounge, LoungeAccess
from .serializers import LoungeDetailSerializer, LoungeListSerializer, LoungeAccessDetailSerializer, LoungeAccessListSerializer

from rest_framework.permissions import IsAuthenticated, IsAdminUser, SAFE_METHODS


class IsAdminOrReadOnly(IsAdminUser):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return super().has_permission(request, view)


class LoungeViewSet(viewsets.ModelViewSet):
    queryset = Lounge.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == "list":
            return LoungeListSerializer
        
        if self.action == "retrieve":
            return LoungeDetailSerializer
        
        return LoungeDetailSerializer


class LoungeAccessViewSet(viewsets.ModelViewSet):
    queryset = LoungeAccess.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return LoungeAccess.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return LoungeAccessListSerializer
        
        if self.action == "retrieve":
            return LoungeAccessDetailSerializer
        
        return LoungeAccessDetailSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
 