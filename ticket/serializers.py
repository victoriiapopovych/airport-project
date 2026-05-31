from rest_framework import serializers
from .models import Booking, Ticket
from flight.models import FlightSeat

from django.db import transaction
from django.utils import timezone


def release_expired_hold(flight_seat):
    if (
        flight_seat.status == FlightSeat.Status.HELD
        and flight_seat.held_until
        and flight_seat.held_until < timezone.now()
    ):
        flight_seat.status = FlightSeat.Status.AVAILABLE
        flight_seat.held_until = None
        flight_seat.held_by = None
        flight_seat.save()

def expire_booking(booking):
    if booking.status != Booking.Status.PENDING:
        return

    expired_seats = booking.tickets.filter(
        flight_seat__status=FlightSeat.Status.HELD,
        flight_seat__held_until__lt=timezone.now(),
    )

    if not expired_seats.exists():
        return

    booking.status = Booking.Status.EXPIRED
    booking.save()

    for ticket in booking.tickets.all():
        ticket.status = Ticket.Status.CANCELLED
        ticket.save()

        flight_seat = ticket.flight_seat
        flight_seat.status = FlightSeat.Status.AVAILABLE
        flight_seat.held_until = None
        flight_seat.held_by = None
        flight_seat.save()


class BookingDetailSerializer(serializers.ModelSerializer):
    user_name = serializers.StringRelatedField(source="user", read_only=True)

    class Meta:
        model = Booking
        fields = ["id", "user", "user_name", "created_at", "status", "total_price"]
        read_only_fields = ["user", "created_at", "status", "total_price"]
    


class BookingListSerializer(serializers.ModelSerializer):
    user_name = serializers.StringRelatedField(source="user", read_only=True)

    class Meta:
        model = Booking
        fields = ["id", "user_name", "created_at", "status", "total_price"]



class TicketDetailSerializer(serializers.ModelSerializer):
    flight_number = serializers.CharField(source="flight_seat.flight.flight_number", read_only=True)
    seat_number = serializers.SerializerMethodField()
    seat_class = serializers.CharField(source="flight_seat.airplane_seat.seat_class.get_class_type_display", read_only=True)

    class Meta:
        model = Ticket
        fields = ["id", "booking", "flight_seat", "flight_number", "seat_number", "seat_class", "passenger_first_name", "passenger_last_name", "price", "status"]
        read_only_fields = ["price", "status"]

    def get_seat_number(self, obj):
        return f"{obj.flight_seat.airplane_seat.row_number}{obj.flight_seat.airplane_seat.seat_letter}"

    
    
class TicketListSerializer(serializers.ModelSerializer):
    flight_number = serializers.CharField(source="flight_seat.flight.flight_number", read_only=True)
    seat_number = serializers.SerializerMethodField()
    seat_class = serializers.CharField(source="flight_seat.airplane_seat.seat_class.get_class_type_display", read_only=True)

    class Meta:
        model = Ticket
        fields = ["id", "flight_number", "seat_number", "seat_class", "passenger_first_name", "passenger_last_name", "price", "status"]

    def get_seat_number(self, obj):
        return f"{obj.flight_seat.airplane_seat.row_number}{obj.flight_seat.airplane_seat.seat_letter}"
    

class BookingStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ["status"]

class TicketStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["status"]

class BookingManagerAdminUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ["status"]


class TicketCreateItemSerializer(serializers.Serializer):
    flight_seat = serializers.PrimaryKeyRelatedField(queryset=FlightSeat.objects.all())
    passenger_first_name = serializers.CharField(max_length=100)
    passenger_last_name = serializers.CharField(max_length=100)

    def validate_passenger_first_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Passenger first name cannot be empty.")

        return value

    def validate_passenger_last_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Passenger last name cannot be empty.")

        return value
    

MAX_TICKETS_PER_BOOKING = 10


class BookingCreateSerializer(serializers.ModelSerializer):
    tickets = TicketCreateItemSerializer(many=True)

    class Meta:
        model = Booking
        fields = ["id", "tickets"]
        read_only_fields = ["id"]

    def validate(self, attrs):
        user = self.context["request"].user

        pending_bookings = Booking.objects.filter(
            user=user,
            status=Booking.Status.PENDING,
        )

        for booking in pending_bookings:
            expire_booking(booking)

        if Booking.objects.filter(
            user=user,
            status=Booking.Status.PENDING,
        ).exists():
            raise serializers.ValidationError(
                "You already have a pending booking."
            )

        return attrs

    def validate_tickets(self, tickets):
        if not tickets:
            raise serializers.ValidationError("At least one ticket is required.")
        

        if len(tickets) > MAX_TICKETS_PER_BOOKING:
            raise serializers.ValidationError(f"You can book maximum {MAX_TICKETS_PER_BOOKING} tickets at once.")


        flight_seats = [item["flight_seat"] for item in tickets]

        if len(flight_seats) != len(set(flight_seats)):
            raise serializers.ValidationError("You cannot book the same seat twice.")
        

        flight_ids = {flight_seat.flight_id for flight_seat in flight_seats}

        if len(flight_ids) > 1:
            raise serializers.ValidationError("All seats in one booking must belong to the same flight.")
        

        flight = flight_seats[0].flight

        if flight.status in [
            flight.Status.CANCELLED,
            flight.Status.DEPARTED,
            flight.Status.ARRIVED,
        ]:
            raise serializers.ValidationError(f"Flight {flight.flight_number} is not available for booking.")
        

        if flight.departure_time <= timezone.now():
            raise serializers.ValidationError(f"Flight {flight.flight_number} has already departed.")
        

        for flight_seat in flight_seats:
            release_expired_hold(flight_seat)

            if flight_seat.status != FlightSeat.Status.AVAILABLE:
                raise serializers.ValidationError(f"Seat {flight_seat} is not available.")

        return tickets

    @transaction.atomic
    def create(self, validated_data):
        tickets_data = validated_data.pop("tickets")
        user = self.context["request"].user

        booking = Booking.objects.create(
            user=user,
            status=Booking.Status.PENDING,
        )

        total_price = 0

        for item in tickets_data:
            flight_seat = FlightSeat.objects.select_for_update().get(
                id=item["flight_seat"].id
            )

            release_expired_hold(flight_seat)

            if flight_seat.status != FlightSeat.Status.AVAILABLE:
                raise serializers.ValidationError(f"Seat {flight_seat} is not available.")

            seat_class = flight_seat.airplane_seat.seat_class

            price = flight_seat.flight.base_price + seat_class.extra_price

            Ticket.objects.create(
                booking=booking,
                flight_seat=flight_seat,
                passenger_first_name=item["passenger_first_name"],
                passenger_last_name=item["passenger_last_name"],
                price=price,
                status=Ticket.Status.PENDING,
            )

            flight_seat.status = FlightSeat.Status.HELD
            flight_seat.held_until = timezone.now() + timezone.timedelta(minutes=15)
            flight_seat.held_by = user
            flight_seat.save()

            total_price += price

        booking.total_price = total_price
        booking.save()

        return booking