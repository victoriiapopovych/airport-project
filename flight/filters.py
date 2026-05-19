import django_filters
from .models import Route, Flight


class RouteFilter(django_filters.FilterSet):
    departure_airport = django_filters.NumberFilter(field_name="departure_airport")
    arrival_airport = django_filters.NumberFilter(field_name="arrival_airport")
    min_distance = django_filters.NumberFilter(field_name="distance_km", lookup_expr="gte")
    max_distance = django_filters.NumberFilter(field_name="distance_km", lookup_expr="lte")

    class Meta:
        model = Route
        fields = ["departure_airport", "arrival_airport", "min_distance", "max_distance"]


class FlightFilter(django_filters.FilterSet):
    departure_from = django_filters.DateTimeFilter(field_name="departure_time", lookup_expr="gte")
    departure_to = django_filters.DateTimeFilter(field_name="departure_time", lookup_expr="lte")
    arrival_from = django_filters.DateTimeFilter(field_name="arrival_time", lookup_expr="gte")
    arrival_to = django_filters.DateTimeFilter(field_name="arrival_time", lookup_expr="lte")

    min_price = django_filters.NumberFilter(field_name="base_price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="base_price", lookup_expr="lte")

    class Meta:
        model = Flight
        fields = ["route", "airline", "airplane", "status", "departure_from", "departure_to", "arrival_from", "arrival_to", "min_price", "max_price"]