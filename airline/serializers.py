from rest_framework import serializers
from .models import Airline, AirplaneType, Airplane


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
 