from rest_framework import serializers
from .models import Country, City, Airport

class CoutrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = ["id", "name", "code"]

class CitySerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(sourse = "country.name", read_only = True)

    class Meta :
        model = City
        fields = ["id", "name", "country", "country_name"]


class AirportSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(sourse = "city.name", read_only = True)
    country_name = serializers.CharField(sourse = "city.country.name", read_only = True)

    class Meta:
        model = Airport
        fields = ["id", "name", "code", "city", "city_name", "country_name"]