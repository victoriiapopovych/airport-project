from rest_framework import viewsets, mixins
from .models import Route, Flight, FlightSeat
from .serializers import RouteListSerializer, RouteDetailSerializer, FlightListSerializer, FlightDetailSerializer, FlightSeatListSerializer, FlightSeatDetailSerializer

from config.permissions import IsManagerOrAdminOrReadOnly

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from .filters import RouteFilter, FlightFilter
from config.pagination import CustomPagination

import logging
logger = logging.getLogger(__name__)


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
    
    def perform_create(self, serializer):
        route = serializer.save()

        logger.info(
            "Route %s was created by user %s.",
            route,
            self.request.user.id if self.request.user.is_authenticated else "anonymous",
        )

    def perform_update(self, serializer):
        route = serializer.save()

        logger.info(
            "Route %s was updated by user %s.",
            route,
            self.request.user.id if self.request.user.is_authenticated else "anonymous",
        )

    def perform_destroy(self, instance):
        route_name = str(instance)
        user_id = self.request.user.id if self.request.user.is_authenticated else "anonymous"

        instance.delete()

        logger.warning(
            "Route %s was deleted by user %s.",
            route_name,
            user_id,
        )


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

    def perform_create(self, serializer):
        flight = serializer.save()

        logger.info(
            "Flight %s was created by user %s.",
            flight.flight_number,
            self.request.user.id if self.request.user.is_authenticated else "anonymous",
        )

    def perform_update(self, serializer):
        flight = serializer.save()

        logger.info(
            "Flight %s was updated by user %s.",
            flight.flight_number,
            self.request.user.id if self.request.user.is_authenticated else "anonymous",
        )

    def perform_destroy(self, instance):
        flight_number = instance.flight_number
        user_id = self.request.user.id if self.request.user.is_authenticated else "anonymous"

        instance.delete()

        logger.warning(
            "Flight %s was deleted by user %s.",
            flight_number,
            user_id,
        )
    

class FlightSeatViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = FlightSeat.objects.all()
    permission_classes = [IsManagerOrAdminOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["flight", "airplane_seat", "status"]
    search_fields = ["flight__flight_number", "airplane_seat__seat_letter"]

    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == "list":
            return FlightSeatListSerializer

        return FlightSeatDetailSerializer
