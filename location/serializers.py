from rest_framework import serializers
from .models import Country, City, Airport

class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = ["id", "name", "code"]

class CitySerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source = "country.name", read_only = True)

    class Meta :
        model = City
        fields = ["id", "name", "country", "country_name"]


class AirportDetailSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source = "city.name", read_only = True)
    country_name = serializers.CharField(source = "city.country.name", read_only = True)

    class Meta:
        model = Airport
        fields = ["id", "name", "code", "city", "city_name", "country_name"]


class AirportListSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source="city.name", read_only=True)

    class Meta:
        model = Airport
        fields = ["id", "name", "code", "city_name"]
