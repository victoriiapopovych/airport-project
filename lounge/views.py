from rest_framework import viewsets
from .models import Lounge, LoungeAccess
from .serializers import LoungeDetailSerializer, LoungeListSerializer, LoungeAccessDetailSerializer, LoungeAccessListSerializer


class LoungeViewSet(viewsets.ModelViewSet):
    queryset = Lounge.objects.all()
    
    def get_serializer_class(self):
        if self.action == "list":
            return LoungeListSerializer
        
        if self.action == "retrieve":
            return LoungeDetailSerializer
        
        return LoungeDetailSerializer


class LoungeAccessViewSet(viewsets.ModelViewSet):
    queryset = LoungeAccess.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return LoungeAccessListSerializer
        
        if self.action == "retrieve":
            return LoungeAccessDetailSerializer
        
        return LoungeAccessDetailSerializer
