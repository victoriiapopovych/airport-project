from rest_framework import viewsets, generics
from .models import Airline, AirplaneType, Airplane
from .serializers import AirlineListSerializer, AirlineDetailSerializer, AirplaneTypeSerializer, AirplaneListSerializer, AirplaneDetailSerializer

from rest_framework.permissions import IsAdminUser, SAFE_METHODS


class IsAdminOrReadOnly(IsAdminUser):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return super().has_permission(request, view)


class AirlineViewSet(viewsets.ModelViewSet):
    queryset = Airline.objects.all()
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action == "list":
            return AirlineListSerializer

        if self.action == "retrieve":
            return AirlineDetailSerializer
        
        return AirlineDetailSerializer


class AirplaneTypeListCreateAPIView(generics.ListCreateAPIView):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = [IsAdminOrReadOnly]

class AirplaneTypeRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = [IsAdminOrReadOnly]


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
    
        if self.action == "retrieve":
            return AirplaneDetailSerializer
        
        return AirplaneDetailSerializer

