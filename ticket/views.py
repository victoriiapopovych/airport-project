from rest_framework.response import Response
from rest_framework import viewsets, mixins

from .models import Booking, Ticket
from .serializers import BookingListSerializer, BookingDetailSerializer, BookingCreateSerializer, TicketListSerializer, TicketDetailSerializer

from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .permissions import CanViewAllBookings, CanCreateBooking, CanCancelBooking
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from config.pagination import CustomPagination

from .services import cancel_booking

import logging
logger = logging.getLogger(__name__)

 
class BookingViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Booking.objects.all()
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["status", "user", "created_at"]
    search_fields = ["user__email", "user__first_name", "user__last_name"]

    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = Booking.objects.prefetch_related("tickets", "tickets__flight", "tickets__airplane_seat", "tickets__airplane_seat__seat_class")

        if CanViewAllBookings().has_permission(self.request, self):
            return queryset

        return queryset.filter(user=self.request.user)

    def get_permissions(self):
        if self.action == "create":
            return [CanCreateBooking()]

        if self.action == "cancel":
            return [CanCancelBooking()]

        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "list":
            return BookingListSerializer

        if self.action == "create":
            return BookingCreateSerializer

        return BookingDetailSerializer

    def perform_create(self, serializer):
        booking = serializer.save()

        logger.info("Booking %s was created by user %s through API.", booking.id, self.request.user.id)

    @extend_schema(request=None)
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        booking = self.get_object()

        if booking.status != Booking.Status.PENDING:
            raise PermissionDenied("Only pending booking can be cancelled.")

        cancel_booking(booking)

        serializer = BookingDetailSerializer(booking)
        return Response(serializer.data)


class TicketViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ticket.objects.all()
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["status", "booking", "flight", "airplane_seat"]
    search_fields = ["passenger_first_name", "passenger_last_name", "flight__flight_number", "airplane_seat__seat_letter"]

    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = Ticket.objects.select_related("booking", "booking__user", "flight", "airplane_seat", "airplane_seat__seat_class")

        if CanViewAllBookings().has_permission(self.request, self):
            return queryset

        return queryset.filter(booking__user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer
        
        return TicketDetailSerializer