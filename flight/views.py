from rest_framework import viewsets

from .models import Route, Flight
from .serializers import RouteListSerializer, RouteDetailSerializer, FlightListSerializer, FlightDetailSerializer, AvailableSeatSerializer
from .services import get_available_seats_for_flight

from rest_framework.decorators import action
from rest_framework.response import Response

from config.permissions import IsManagerOrAdminOrReadOnly

from .filters import RouteFilter, FlightFilter
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from config.pagination import CustomPagination

import logging
logger = logging.getLogger(__name__)


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related("departure_airport", "arrival_airport")
    permission_classes = [IsManagerOrAdminOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = RouteFilter
    search_fields = [
        "departure_airport__name",
        "departure_airport__code",
        "arrival_airport__name",
        "arrival_airport__code",
    ]
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        return RouteDetailSerializer

    def perform_create(self, serializer):
        route = serializer.save()
        logger.info("Route %s was created by user %s.", route, self.request.user.id if self.request.user.is_authenticated else "anonymous")

    def perform_update(self, serializer):
        route = serializer.save()
        logger.info("Route %s was updated by user %s.", route, self.request.user.id if self.request.user.is_authenticated else "anonymous")

    def perform_destroy(self, instance):
        route_name = str(instance)
        user_id = self.request.user.id if self.request.user.is_authenticated else "anonymous"
        instance.delete()
        logger.warning("Route %s was deleted by user %s.", route_name, user_id)


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.select_related(
        "route",
        "route__departure_airport",
        "route__arrival_airport",
        "airline",
        "airplane",
    )
    permission_classes = [IsManagerOrAdminOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = FlightFilter
    search_fields = [
        "flight_number",
        "route__departure_airport__name",
        "route__arrival_airport__name",
        "airline__name",
        "airplane__tail_number",
    ]
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer

        if self.action == "available_seats":
            return AvailableSeatSerializer

        return FlightDetailSerializer

    @action(detail=True, methods=["get"], url_path="available-seats")
    def available_seats(self, request, pk=None):
        flight = self.get_object()
        seats = get_available_seats_for_flight(flight)

        page = self.paginate_queryset(seats)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={"flight": flight})
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(seats, many=True, context={"flight": flight})
        return Response(serializer.data)

    def perform_create(self, serializer):
        flight = serializer.save()
        logger.info("Flight %s was created by user %s.", flight.flight_number, self.request.user.id if self.request.user.is_authenticated else "anonymous")

    def perform_update(self, serializer):
        flight = serializer.save()
        logger.info("Flight %s was updated by user %s.", flight.flight_number, self.request.user.id if self.request.user.is_authenticated else "anonymous")

    def perform_destroy(self, instance):
        flight_number = instance.flight_number
        user_id = self.request.user.id if self.request.user.is_authenticated else "anonymous"
        instance.delete()
        logger.warning("Flight %s was deleted by user %s.", flight_number, user_id)