from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.shortcuts import get_object_or_404

from .models import TicketClass, Booking, Ticket
from .serializers import TicketClassSerializer, BookingListSerializer, BookingDetailSerializer, TicketListSerializer, TicketDetailSerializer, BookingStatusUpdateSerializer, TicketStatusUpdateSerializer, BookingManagerAdminUpdateSerializer

from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from user.models import User
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from user.permissions import IsManagerOrAdminOrReadOnly
from django.db import models

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from config.pagination import CustomPagination


class TicketClassListCreateAPIView(APIView):
    serializer_class = TicketClassSerializer
    permission_classes = [IsManagerOrAdminOrReadOnly]

    def get(self, request):
        ticket_classes = TicketClass.objects.all()
        serializer = TicketClassSerializer(ticket_classes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TicketClassSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TicketClassDetailAPIView(APIView):
    serializer_class = TicketClassSerializer
    permission_classes = [IsManagerOrAdminOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(TicketClass, pk=pk)

    def get(self, request, pk):
        ticket_class = self.get_object(pk)
        serializer = TicketClassSerializer(ticket_class)
        return Response(serializer.data)

    def put(self, request, pk):
        ticket_class = self.get_object(pk)
        serializer = TicketClassSerializer(ticket_class, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        ticket_class = self.get_object(pk)
        serializer = TicketClassSerializer(ticket_class, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        ticket_class = self.get_object(pk)
        ticket_class.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["status", "user"]
    search_fields = ["user__username", "user__email"]

    pagination_class = CustomPagination

    def get_queryset(self):
        if (self.request.user.is_staff or self.request.user.is_superuser
            or self.request.user.role == User.Role.SUPPORT
            or self.request.user.role == User.Role.MANAGER):
            
            return Booking.objects.all()
        
        return Booking.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return BookingListSerializer

        if self.action == "retrieve":
            return BookingDetailSerializer

        if self.action in ["update", "partial_update"]:
            return BookingManagerAdminUpdateSerializer

        if self.action == "update_status":
            return BookingStatusUpdateSerializer

        return BookingDetailSerializer
    
    def perform_create(self, serializer):
        user = self.request.user

        if user.role in [
            User.Role.SUPPORT,
            User.Role.MANAGER,
        ]:
            raise PermissionDenied(
                "Support and manager cannot create bookings."
            )

        if user.is_staff or user.is_superuser:
            serializer.save(user=user)
            return

        if not user.is_verified:
            raise PermissionDenied("Only verified users can create bookings.")

        serializer.save(user=user)

    def perform_update(self, serializer):
        if not (self.request.user.is_staff or self.request.user.is_superuser
            or self.request.user.role == User.Role.MANAGER
        ):
            raise PermissionDenied("Only manager or admin can update booking.")

        serializer.save()

    def perform_destroy(self, instance):
        if not (self.request.user.is_staff or self.request.user.is_superuser
                or self.request.user.role == User.Role.MANAGER):
            raise PermissionDenied("Only admin and manager can delete this object.")

        instance.delete()
    
    @extend_schema(request=None)
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        booking = self.get_object()

        if (
            booking.user != request.user
            and not (
                request.user.is_staff
                or request.user.is_superuser
                or request.user.role in [
                    User.Role.SUPPORT,
                    User.Role.MANAGER,
                ]
            )
        ):
            raise PermissionDenied("You cannot cancel another user's booking.")

        booking.status = Booking.Status.CANCELLED
        booking.save()

        booking.tickets.update(status=Ticket.Status.CANCELLED)

        serializer = BookingDetailSerializer(booking)
        return Response(serializer.data)
    
    @action(detail=True, methods=["patch"], url_path="status")
    def update_status(self, request, pk=None):
        booking = self.get_object()

        if not (
            request.user.is_staff
            or request.user.is_superuser
            or request.user.role == User.Role.SUPPORT
            or request.user.role == User.Role.MANAGER
        ):
            raise PermissionDenied("Only support, manager or admin can update booking status.")

        serializer = BookingStatusUpdateSerializer(
            booking,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

  
class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["status", "booking", "flight", "ticket_class"]
    search_fields = ["passenger_first_name", "passenger_last_name", "seat_number", "flight__flight_number"]

    pagination_class = CustomPagination

    def get_queryset(self):
        if (
            self.request.user.is_staff
            or self.request.user.is_superuser
            or self.request.user.role == User.Role.SUPPORT
            or self.request.user.role == User.Role.MANAGER
        ):
            return Ticket.objects.all()

        return Ticket.objects.filter(booking__user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer

        if self.action == "retrieve":
            return TicketDetailSerializer

        if self.action in ["update", "partial_update"]:
            return TicketDetailSerializer

        if self.action == "update_status":
            return TicketStatusUpdateSerializer

        return TicketDetailSerializer

    def perform_create(self, serializer):
        user = self.request.user
        booking = serializer.validated_data["booking"]
        flight = serializer.validated_data["flight"]
        ticket_class = serializer.validated_data["ticket_class"]

        ticket_price = flight.base_price + ticket_class.extra_price

        if user.is_staff or user.is_superuser or user.role in [
            User.Role.SUPPORT,
            User.Role.MANAGER,
        ]:
            ticket = serializer.save(price=ticket_price)
            self.update_booking_total_price(ticket.booking)
            return

        if not user.is_verified:
            raise PermissionDenied("Only verified users can create tickets.")

        if booking.user != user:
            raise PermissionDenied("You cannot create ticket for another user's booking.")

        ticket = serializer.save(price=ticket_price)
        self.update_booking_total_price(ticket.booking)

    def perform_update(self, serializer):
        if not (
            self.request.user.is_staff
            or self.request.user.is_superuser
            or self.request.user.role == User.Role.MANAGER
        ):
            raise PermissionDenied("Only manager or admin can update ticket.")

        ticket = serializer.save()

        ticket.price = (
            ticket.flight.base_price
            + ticket.ticket_class.extra_price
        )

        ticket.save()

        self.update_booking_total_price(ticket.booking)

    def update_booking_total_price(self, booking):
        total_price = booking.tickets.aggregate(
            total=models.Sum("price")
        )["total"] or 0

        booking.total_price = total_price
        booking.save()

    def perform_destroy(self, instance):
        if not (
            self.request.user.is_staff
            or self.request.user.is_superuser
            or self.request.user.role == User.Role.MANAGER
        ):
            raise PermissionDenied("Only admin and manager can delete this object.")

        booking = instance.booking
        instance.delete()
        self.update_booking_total_price(booking)


    @extend_schema(request=None)
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        ticket = self.get_object()

        if (
            ticket.booking.user != request.user
            and not (
                request.user.is_staff
                or request.user.is_superuser
                or request.user.role in [
                    User.Role.SUPPORT,
                    User.Role.MANAGER,
                ]
            )
        ):
            raise PermissionDenied("You cannot cancel another user's ticket.")

        ticket.status = Ticket.Status.CANCELLED
        ticket.save()

        serializer = TicketDetailSerializer(ticket)
        return Response(serializer.data)

    @action(detail=True, methods=["patch"], url_path="status")
    def update_status(self, request, pk=None):
        ticket = self.get_object()

        if not (
            request.user.is_staff
            or request.user.is_superuser
            or request.user.role == User.Role.SUPPORT
            or request.user.role == User.Role.MANAGER
        ):
            raise PermissionDenied("Only support, manager or admin can update ticket status.")

        serializer = TicketStatusUpdateSerializer(
            ticket,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
