from rest_framework import serializers

from airline.models import AirplaneSeat
from flight.models import Flight
from .models import Booking, Ticket

from .services import create_booking
from .validators import validate_available_seats, validate_duplicate_seats, validate_flight_departure, validate_flight_status, validate_passenger_name, validate_same_flight, validate_seats_belong_to_flight_airplane, validate_ticket_limit


class TicketListSerializer(serializers.ModelSerializer):
    flight_number = serializers.CharField(source="flight.flight_number", read_only=True)
    seat_number = serializers.CharField(source="airplane_seat.seat_number", read_only=True)
    seat_class = serializers.CharField(source="airplane_seat.seat_class.get_class_type_display", read_only=True)

    class Meta:
        model = Ticket
        fields = ["id", "flight_number", "seat_number", "seat_class", "passenger_first_name", "passenger_last_name", "price", "status"]


class TicketDetailSerializer(serializers.ModelSerializer):
    flight_number = serializers.CharField(source="flight.flight_number", read_only=True)
    seat_number = serializers.CharField(source="airplane_seat.seat_number", read_only=True)
    seat_class = serializers.CharField(source="airplane_seat.seat_class.get_class_type_display", read_only=True)

    class Meta:
        model = Ticket
        fields = ["id", "booking", "flight", "airplane_seat", "flight_number", "seat_number", "seat_class", "passenger_first_name", "passenger_last_name", "price", "status"]
        read_only_fields = ["price", "status"]


class BookingListSerializer(serializers.ModelSerializer):
    user_name = serializers.StringRelatedField(source="user", read_only=True)

    class Meta:
        model = Booking
        fields = ["id", "user_name", "created_at", "status", "total_price"]


class BookingDetailSerializer(serializers.ModelSerializer):
    user_name = serializers.StringRelatedField(source="user", read_only=True)
    tickets = TicketListSerializer(many=True, read_only=True)

    class Meta:
        model = Booking
        fields = ["id", "user", "user_name", "created_at", "status", "total_price", "tickets"]
        read_only_fields = ["user", "created_at", "status", "total_price"]


class TicketCreateItemSerializer(serializers.Serializer):
    flight = serializers.PrimaryKeyRelatedField(queryset=Flight.objects.all())
    airplane_seat = serializers.PrimaryKeyRelatedField(queryset=AirplaneSeat.objects.select_related("airplane", "seat_class").all())
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

        if Booking.objects.filter(user=user, status=Booking.Status.PENDING).exists():
            raise serializers.ValidationError("You already have a pending booking.")

        tickets = attrs.get("tickets", [])

        validate_ticket_limit(tickets)
        validate_duplicate_seats(tickets)
        validate_same_flight(tickets)
        validate_seats_belong_to_flight_airplane(tickets)

        flight = tickets[0]["flight"]

        validate_flight_status(flight)
        validate_flight_departure(flight)
        validate_available_seats(tickets)

        return attrs

    def create(self, validated_data):
        tickets_data = validated_data.pop("tickets")
        user = self.context["request"].user

        return create_booking(user, tickets_data)