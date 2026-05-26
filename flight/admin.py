from django.contrib import admin
from .models import Flight, Route, FlightSeat

# Register your models here.
@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("departure_airport", "arrival_airport", "distance_km", "estimated_duration")
    list_filter = ("departure_airport", "arrival_airport")
    search_fields = ("departure_airport__name", "departure_airport__code", "arrival_airport__name", "arrival_airport__code")

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ("flight_number", "route", "airline", "airplane", "departure_time", "arrival_time", "status", "terminal_name", "boarding_gate")
    list_filter = ("status", "airline")
    search_fields = ("flight_number", "airline__name")

@admin.register(FlightSeat)
class FlightSeatAdmin(admin.ModelAdmin):
    list_display = ("flight", "airplane_seat", "status", "reserved_until")
    list_filter = ("flight", "status")
    search_fields = ("flight__flight_number", "airplane_seat__seat_letter")