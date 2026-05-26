from rest_framework import serializers
from .models import Airline, AirplaneType, Airplane, SeatClass, AirplaneSeat


class AirlineDetailSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source="country.name", read_only=True)

    class Meta:
        model = Airline
        fields = ["id", "name", "iata_code", "country", "country_name", "is_active", "airports"]


class AirlineListSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source="country.name", read_only=True)

    class Meta:
        model = Airline
        fields = ["id", "name", "iata_code", "country_name"]


class AirplaneTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = AirplaneType
        fields = ["id", "manufacturer", "code"]


class AirplaneDetailSerializer(serializers.ModelSerializer):
    airline_name = serializers.CharField(source="airline.name", read_only=True)
    airplane_type_name = serializers.StringRelatedField(source="airplane_type", read_only=True)

    class Meta:
        model = Airplane
        fields = ["id", "tail_number", "airline", "airline_name", "airplane_type", "airplane_type_name", "manufactured_year", "num_of_passengers", "crew_count", "is_active"]


class AirplaneListSerializer(serializers.ModelSerializer):
    airline_name = serializers.CharField(source="airline.name", read_only=True)
    airplane_type_name = serializers.StringRelatedField(source="airplane_type", read_only=True)

    class Meta:
        model = Airplane
        fields = ["id", "tail_number", "airline_name", "airplane_type_name", "num_of_passengers"]


class SeatClassSerializer(serializers.ModelSerializer):
    airline_name = serializers.CharField(source="airline.name", read_only=True)

    class Meta:
        model = SeatClass
        fields = ["id", "airline", "airline_name", "class_type", "extra_price", "baggage_kg", "priority_boarding", "lounge_access"]


class AirplaneSeatListSerializer(serializers.ModelSerializer):
    airplane_tail_number = serializers.CharField(source="airplane.tail_number", read_only=True)
    seat_class_name = serializers.CharField(source="seat_class.get_class_type_display", read_only=True)

    class Meta:
        model = AirplaneSeat
        fields = ["id", "airplane_tail_number", "row_number", "seat_letter", "seat_class_name", "is_active"]


class AirplaneSeatDetailSerializer(serializers.ModelSerializer):
    airplane_tail_number = serializers.CharField(source="airplane.tail_number", read_only=True)
    seat_class_name = serializers.CharField(source="seat_class.get_class_type_display", read_only=True)

    class Meta:
        model = AirplaneSeat
        fields = ["id", "airplane", "airplane_tail_number", "seat_class", "seat_class_name", "row_number", "seat_letter", "is_window", "is_aisle", "is_exit_row", "has_extra_legroom", "is_active"]
 