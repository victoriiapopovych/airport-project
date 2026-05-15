from rest_framework import viewsets
from .models import User
from .serializers import UserListSerializer, UserDetailSerializer

from rest_framework.permissions import IsAuthenticated


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return User.objects.all()
        
        return User.objects.filter(id=self.request.user.id)
    
    def get_serializer_class(self):
        if self.action == "list":
            return UserListSerializer
        
        if self.action == "retrieve":
            return UserDetailSerializer
        
        return UserDetailSerializer
 