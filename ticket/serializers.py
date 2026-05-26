from rest_framework import serializers
from .models import Booking, Ticket
from flight.models import FlightSeat

from django.db import transaction
from django.utils import timezone


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


class BookingCreateSerializer(serializers.ModelSerializer):
    tickets = TicketCreateItemSerializer(many=True)

    class Meta:
        model = Booking
        fields = ["id", "tickets"]
        read_only_fields = ["id"]

    def validate_tickets(self, tickets):
        request = self.context["request"]

        if not tickets:
            raise serializers.ValidationError("At least one ticket is required.")

        flight_seats = [item["flight_seat"] for item in tickets]

        if len(flight_seats) != len(set(flight_seats)):
            raise serializers.ValidationError("You cannot book the same seat twice.")

        for flight_seat in flight_seats:
            if (
                flight_seat.status == FlightSeat.Status.RESERVED
                and flight_seat.reserved_until is not None
                and flight_seat.reserved_until < timezone.now()
            ):
                flight_seat.status = FlightSeat.Status.AVAILABLE
                flight_seat.reserved_until = None
                flight_seat.reserved_by = None
                flight_seat.save()

                raise serializers.ValidationError(f"Reservation for seat {flight_seat} has expired.")

            if flight_seat.status != FlightSeat.Status.RESERVED:
                raise serializers.ValidationError(f"Seat {flight_seat} is not reserved.")

            if flight_seat.reserved_by != request.user:
                raise serializers.ValidationError(f"Seat {flight_seat} is reserved by another user.")

        return tickets

    @transaction.atomic
    def create(self, validated_data):
        tickets_data = validated_data.pop("tickets")
        user = self.context["request"].user

        booking = Booking.objects.create(user=user)

        total_price = 0

        for item in tickets_data:
            flight_seat = item["flight_seat"]
            seat_class = flight_seat.airplane_seat.seat_class

            price = flight_seat.flight.base_price + seat_class.extra_price

            Ticket.objects.create(booking=booking, flight_seat=flight_seat, passenger_first_name=item["passenger_first_name"], passenger_last_name=item["passenger_last_name"], price=price)

            flight_seat.status = FlightSeat.Status.SOLD
            flight_seat.reserved_until = None
            flight_seat.reserved_by = None
            flight_seat.save()

            total_price += price

        booking.total_price = total_price
        booking.save()

        return booking