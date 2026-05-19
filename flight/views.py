from rest_framework import viewsets
from .models import Route, Flight
from .serializers import RouteListSerializer, RouteDetailSerializer, FlightListSerializer, FlightDetailSerializer

from user.permissions import IsManagerOrAdminOrReadOnly

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from .filters import RouteFilter, FlightFilter

from config.pagination import CustomPagination


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    permission_classes = [IsManagerOrAdminOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = RouteFilter
    search_fields = ["departure_airport__name","departure_airport__code","arrival_airport__name","arrival_airport__code"]

    pagination_class = CustomPagination
    
    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        
        if self.action == "retrieve":
            return RouteDetailSerializer
        
        return RouteDetailSerializer


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    permission_classes = [IsManagerOrAdminOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = FlightFilter
    search_fields = ["flight_number", "route__departure_airport__name", "route__arrival_airport__name", "airline__name", "airplane__tail_number"]

    pagination_class = CustomPagination
    
    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        
        if self.action == "retrieve":
            return FlightDetailSerializer
        
        return FlightDetailSerializer
 