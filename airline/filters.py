import django_filters
from .models import Airline, AirplaneType, Airplane


class AirlineFilter(django_filters.FilterSet):
    airport = django_filters.NumberFilter(field_name="airports__id")

    class Meta:
        model = Airline
        fields = ["country", "is_active", "airport"]


class AirplaneTypeFilter(django_filters.FilterSet):
    manufacturer = django_filters.CharFilter(field_name="manufacturer", lookup_expr="icontains")

    class Meta:
        model = AirplaneType
        fields = ["manufacturer"]


class AirplaneFilter(django_filters.FilterSet):
    manufactured_year_from = django_filters.NumberFilter(field_name="manufactured_year", lookup_expr="gte")
    manufactured_year_to = django_filters.NumberFilter(field_name="manufactured_year", lookup_expr="lte")
    min_passengers = django_filters.NumberFilter(field_name="num_of_passengers", lookup_expr="gte")

    class Meta:
        model = Airplane
        fields = ["airline", "airplane_type", "is_active", "manufactured_year_from", "manufactured_year_to", "min_passengers"]