from rest_framework.response import Response
from rest_framework import viewsets

from .models import Booking, Ticket
from .serializers import BookingListSerializer, BookingDetailSerializer, BookingCreateSerializer, TicketListSerializer, TicketDetailSerializer

from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from user.models import User

from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from config.pagination import CustomPagination

from flight.models import FlightSeat


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["status", "user", "created_at"]
    search_fields = ["user__email", "user__first_name", "user__last_name"]

    pagination_class = CustomPagination

    def is_admin(self, user):
        return user.is_staff or user.is_superuser

    def is_support_or_manager_or_admin(self, user):
        return (
            self.is_admin(user)
            or user.role in [
                User.Role.SUPPORT,
                User.Role.MANAGER,
            ]
        )

    def get_queryset(self):
        if self.is_support_or_manager_or_admin(self.request.user):
            return Booking.objects.all()
        
        return Booking.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return BookingListSerializer

        if self.action == "create":
            return BookingCreateSerializer

        return BookingDetailSerializer
    
    def perform_create(self, serializer):
        user = self.request.user

        if user.role in [
            User.Role.SUPPORT,
            User.Role.MANAGER,
        ]:
            raise PermissionDenied("Support and manager cannot create bookings.")

        if self.is_admin(user):
            serializer.save()
            return

        if not user.is_verified:
            raise PermissionDenied("Only verified users can create bookings.")

        serializer.save()

    def perform_update(self, serializer):
        raise PermissionDenied("Booking cannot be updated directly. Use status or cancel action.")

    def perform_destroy(self, instance):
        raise PermissionDenied("Booking cannot be deleted. Use cancel action.")

    @extend_schema(request=None)
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        booking = self.get_object()

        if (
            booking.user != request.user
            and not self.is_support_or_manager_or_admin(request.user)
        ):
            raise PermissionDenied("You cannot cancel another user's booking.")
        
        if booking.status == Booking.Status.CANCELLED:
            raise PermissionDenied("Booking is already cancelled.")

        booking.status = Booking.Status.CANCELLED
        booking.save()

        for ticket in booking.tickets.all():
            ticket.status = Ticket.Status.CANCELLED
            ticket.save()

            flight_seat = ticket.flight_seat
            flight_seat.status = FlightSeat.Status.AVAILABLE
            flight_seat.reserved_until = None
            flight_seat.reserved_by = None
            flight_seat.save()

        serializer = BookingDetailSerializer(booking)
        return Response(serializer.data)

  
class TicketViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ticket.objects.all()
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["status", "booking", "flight_seat", "flight_seat__flight"]
    search_fields = ["passenger_first_name", "passenger_last_name", "flight_seat__flight__flight_number", "flight_seat__airplane_seat__seat_letter"]

    pagination_class = CustomPagination

    def is_admin(self, user):
        return user.is_staff or user.is_superuser

    def is_support_or_manager_or_admin(self, user):
        return (
            self.is_admin(user)
            or user.role in [
                User.Role.SUPPORT,
                User.Role.MANAGER,
            ]
        )

    def get_queryset(self):
        if self.is_support_or_manager_or_admin(self.request.user):
            return Ticket.objects.all()

        return Ticket.objects.filter(booking__user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer

        return TicketDetailSerializer