from rest_framework import viewsets
from .models import Route, Flight, FlightSeat
from .serializers import RouteListSerializer, RouteDetailSerializer, FlightListSerializer, FlightDetailSerializer, FlightSeatListSerializer, FlightSeatDetailSerializer, FlightSeatReserveSerializer

from user.permissions import IsManagerOrAdminOrReadOnly
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from user.models import User

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from .filters import RouteFilter, FlightFilter
from config.pagination import CustomPagination

from rest_framework.decorators import action


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
        
        return FlightDetailSerializer
    

class FlightSeatViewSet(viewsets.ModelViewSet):
    queryset = FlightSeat.objects.all()
    permission_classes = [IsManagerOrAdminOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["flight", "airplane_seat", "status"]
    search_fields = ["flight__flight_number", "airplane_seat__seat_letter"]

    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == "list":
            return FlightSeatListSerializer

        if self.action == "reserve":
            return FlightSeatReserveSerializer

        return FlightSeatDetailSerializer

    @action(detail=True, methods=["post"])
    def reserve(self, request, pk=None):
        if request.user.role != User.Role.PASSENGER:
            raise PermissionDenied("Only passengers can reserve seats.")

        if not request.user.is_verified:
            raise PermissionDenied("Only verified passengers can reserve seats.")

        flight_seat = self.get_object()

        serializer = self.get_serializer(flight_seat, data={}, partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)