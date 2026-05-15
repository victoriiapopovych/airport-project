from rest_framework import viewsets
from .models import Route, Flight
from .serializers import RouteListSerializer, RouteDetailSerializer, FlightListSerializer, FlightDetailSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    
    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        
        if self.action == "retrieve":
            return RouteDetailSerializer
        
        return RouteDetailSerializer


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    
    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        
        if self.action == "retrieve":
            return FlightDetailSerializer
        
        return FlightDetailSerializer
 