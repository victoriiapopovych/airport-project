from rest_framework import viewsets
from .models import User
from .serializers import UserListSerializer, UserDetailSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    
    def get_serializer_class(self):
        if self.action == "list":
            return UserListSerializer
        
        if self.action == "retrieve":
            return UserDetailSerializer
        
        return UserDetailSerializer
 