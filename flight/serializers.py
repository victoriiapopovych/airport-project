from rest_framework import serializers
from .models import Route, Flight


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

    class Meta:
        model = Flight
        fields = ["id", "flight_number", "route", "route_name", "airline", "airline_name", "airplane", "airplane_tail_number", "departure_time", "arrival_time", "status", "terminal_name", "boarding_gate", "base_price"]


class FlightListSerializer(serializers.ModelSerializer):
    route_name = serializers.StringRelatedField(source="route", read_only=True)
    airline_name = serializers.CharField(source="airline.name", read_only=True)

    class Meta:
        model = Flight
        fields = ["id", "flight_number", "route_name", "airline_name", "departure_time", "arrival_time", "status", "base_price"]

