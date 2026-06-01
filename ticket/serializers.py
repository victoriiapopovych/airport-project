from rest_framework import serializers
from .models import Booking, Ticket
from flight.models import FlightSeat

from django.db import transaction

from .services import expire_booking, create_booking

from .validators import validate_ticket_limit, validate_duplicate_seats, validate_same_flight, validate_flight_status, validate_flight_departure, validate_available_seats, validate_passenger_name


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


class TicketCreateItemSerializer(serializers.Serializer):
    flight_seat = serializers.PrimaryKeyRelatedField(queryset=FlightSeat.objects.all())
    passenger_first_name = serializers.CharField(max_length=100)
    passenger_last_name = serializers.CharField(max_length=100)

    def validate_passenger_first_name(self, value):
        return validate_passenger_name(value, "Passenger first name")

    def validate_passenger_last_name(self, value):
        return validate_passenger_name(value, "Passenger last name")


class BookingCreateSerializer(serializers.ModelSerializer):
    tickets = TicketCreateItemSerializer(many=True)

    class Meta:
        model = Booking
        fields = ["id", "tickets"]
        read_only_fields = ["id"]

    def validate(self, attrs):
        user = self.context["request"].user

        pending_bookings = Booking.objects.filter(user=user, status=Booking.Status.PENDING,)

        for booking in pending_bookings:
            expire_booking(booking)

        if Booking.objects.filter(user=user, status=Booking.Status.PENDING).exists():
            raise serializers.ValidationError("You already have a pending booking.")

        return attrs

    def validate_tickets(self, tickets):
        validate_ticket_limit(tickets)

        flight_seats = [item["flight_seat"] for item in tickets]

        validate_duplicate_seats(flight_seats)
        validate_same_flight(flight_seats)

        flight = flight_seats[0].flight

        validate_flight_status(flight)
        validate_flight_departure(flight)

        validate_available_seats(flight_seats)

        return tickets
    
    @transaction.atomic
    def create(self, validated_data):
        tickets_data = validated_data.pop("tickets")
        user = self.context["request"].user

        return create_booking(user, tickets_data)