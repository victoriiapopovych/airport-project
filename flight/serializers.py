from rest_framework import serializers

from airline.models import AirplaneSeat
from .models import Route, Flight
from .services import (
    calculate_ticket_price,
    get_available_seats_count_for_flight,
)


class RouteDetailSerializer(serializers.ModelSerializer):
    departure_airport_name = serializers.CharField(source="departure_airport.name", read_only=True)
    arrival_airport_name = serializers.CharField(source="arrival_airport.name", read_only=True)

    class Meta:
        model = Route
        fields = ["id", "departure_airport", "departure_airport_name", "arrival_airport", "arrival_airport_name", "distance_km", "estimated_duration"]


class RouteListSerializer(serializers.ModelSerializer):
    departure_airport_name = serializers.CharField(source="departure_airport.name", read_only=True)
    arrival_airport_name = serializers.CharField(source="arrival_airport.name", read_only=True)

    class Meta:
        model = Route
        fields = ["id", "departure_airport_name", "arrival_airport_name", "estimated_duration"]


class FlightDetailSerializer(serializers.ModelSerializer):
    route_name = serializers.StringRelatedField(source="route", read_only=True)
    airline_name = serializers.CharField(source="airline.name", read_only=True)
    airplane_tail_number = serializers.CharField(source="airplane.tail_number", read_only=True)
    available_seats_count = serializers.SerializerMethodField()

    class Meta:
        model = Flight
        fields = [
            "id", "flight_number", "route", "route_name", "airline", "airline_name",
            "airplane", "airplane_tail_number", "departure_time", "arrival_time",
            "status", "terminal_name", "boarding_gate", "base_price",
            "available_seats_count",
        ]

    def get_available_seats_count(self, obj):
        return get_available_seats_count_for_flight(obj)

    def validate(self, attrs):
        airline = attrs.get("airline", getattr(self.instance, "airline", None))
        airplane = attrs.get("airplane", getattr(self.instance, "airplane", None))
        departure_time = attrs.get("departure_time", getattr(self.instance, "departure_time", None))
        arrival_time = attrs.get("arrival_time", getattr(self.instance, "arrival_time", None))

        if airline and airplane and airplane.airline != airline:
            raise serializers.ValidationError({"airplane": "Selected airplane must belong to the selected airline."})

        if airplane and not airplane.seats.exists():
            raise serializers.ValidationError({"airplane": "Seats must be generated for this airplane before creating a flight."})

        if departure_time and arrival_time and arrival_time <= departure_time:
            raise serializers.ValidationError({"arrival_time": "Arrival time must be later than departure time."})

        return attrs


class FlightListSerializer(serializers.ModelSerializer):
    route_name = serializers.StringRelatedField(source="route", read_only=True)
    airline_name = serializers.CharField(source="airline.name", read_only=True)
    available_seats_count = serializers.SerializerMethodField()

    class Meta:
        model = Flight
        fields = [
            "id", "flight_number", "route_name", "airline_name",
            "departure_time", "arrival_time", "status", "base_price",
            "available_seats_count",
        ]

    def get_available_seats_count(self, obj):
        return get_available_seats_count_for_flight(obj)


class AvailableSeatSerializer(serializers.ModelSerializer):
    seat_number = serializers.CharField(read_only=True)
    seat_class = serializers.CharField(source="seat_class.get_class_type_display", read_only=True)
    class_type = serializers.CharField(source="seat_class.class_type", read_only=True)
    ticket_price = serializers.SerializerMethodField()

    class Meta:
        model = AirplaneSeat
        fields = [
            "id", "seat_number", "seat_class", "class_type", "ticket_price",
            "row_number", "seat_letter", "is_window", "is_aisle",
            "is_exit_row", "has_extra_legroom",
        ]

    def get_ticket_price(self, obj):
        flight = self.context["flight"]
        return calculate_ticket_price(flight, obj)