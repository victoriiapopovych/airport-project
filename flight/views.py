from rest_framework import viewsets
from .models import Route, Flight
from .serializers import RouteListSerializer, RouteDetailSerializer, FlightListSerializer, FlightDetailSerializer

from rest_framework.permissions import IsAdminUser, SAFE_METHODS


class IsAdminOrReadOnly(IsAdminUser):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return super().has_permission(request, view)


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        
        if self.action == "retrieve":
            return RouteDetailSerializer
        
        return RouteDetailSerializer


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        
        if self.action == "retrieve":
            return FlightDetailSerializer
        
        return FlightDetailSerializer
 