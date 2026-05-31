from rest_framework import serializers
from .models import Route, Flight, FlightSeat

from .services import build_seat_number, calculate_ticket_price


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
        fields = ["id", "flight_number", "route", "route_name", "airline", "airline_name", "airplane", "airplane_tail_number", "departure_time", "arrival_time", "status", "terminal_name", "boarding_gate", "base_price", "available_seats_count"]

    def get_available_seats_count(self, obj):
        return obj.seats.filter(status=FlightSeat.Status.AVAILABLE).count()


class FlightListSerializer(serializers.ModelSerializer):
    route_name = serializers.StringRelatedField(source="route", read_only=True)
    airline_name = serializers.CharField(source="airline.name", read_only=True)
    available_seats_count = serializers.SerializerMethodField()

    class Meta:
        model = Flight
        fields = ["id", "flight_number", "route_name", "airline_name", "departure_time", "arrival_time", "status", "base_price", "available_seats_count"]

    def get_available_seats_count(self, obj):
        return obj.seats.filter(status=FlightSeat.Status.AVAILABLE).count()


class FlightSeatListSerializer(serializers.ModelSerializer):
    seat_number = serializers.SerializerMethodField()
    seat_class = serializers.CharField(source="airplane_seat.seat_class.get_class_type_display", read_only=True)
    ticket_price = serializers.SerializerMethodField()

    class Meta:
        model = FlightSeat
        fields = ["id", "seat_number", "seat_class", "ticket_price", "status"]

    def get_seat_number(self, obj):
        return build_seat_number(obj)

    def get_ticket_price(self, obj):
        return calculate_ticket_price(obj)


class FlightSeatDetailSerializer(serializers.ModelSerializer):
    seat_number = serializers.SerializerMethodField()
    seat_class = serializers.CharField(source="airplane_seat.seat_class.get_class_type_display", read_only=True)
    airplane_tail_number = serializers.CharField(source="airplane_seat.airplane.tail_number", read_only=True)
    ticket_price = serializers.SerializerMethodField()

    class Meta:
        model = FlightSeat
        fields = ["id", "flight", "airplane_seat", "airplane_tail_number", "seat_number", "seat_class", "ticket_price", "status", "held_until"]

    def get_seat_number(self, obj):
        return build_seat_number(obj)

    def get_ticket_price(self, obj):
        return calculate_ticket_price(obj)
    
