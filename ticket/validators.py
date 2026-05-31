from rest_framework import serializers
from django.utils import timezone

from flight.models import FlightSeat
from .services import release_expired_hold


MAX_TICKETS_PER_BOOKING = 10


def validate_ticket_limit(tickets):
    if not tickets:
        raise serializers.ValidationError("At least one ticket is required.")

    if len(tickets) > MAX_TICKETS_PER_BOOKING:
        raise serializers.ValidationError(f"You can book maximum {MAX_TICKETS_PER_BOOKING} tickets at once.")


def validate_duplicate_seats(flight_seats):
    if len(flight_seats) != len(set(flight_seats)):
        raise serializers.ValidationError("You cannot book the same seat twice.")


def validate_same_flight(flight_seats):
    flight_ids = {seat.flight_id for seat in flight_seats}

    if len(flight_ids) > 1:
        raise serializers.ValidationError("All seats in one booking must belong to the same flight.")


def validate_flight_status(flight):
    if flight.status in [
        flight.Status.CANCELLED,
        flight.Status.DEPARTED,
        flight.Status.ARRIVED,
    ]:
        raise serializers.ValidationError(f"Flight {flight.flight_number} is not available for booking.")


def validate_flight_departure(flight):
    if flight.departure_time <= timezone.now():
        raise serializers.ValidationError(f"Flight {flight.flight_number} has already departed.")


def validate_available_seats(flight_seats):
    for flight_seat in flight_seats:
        release_expired_hold(flight_seat)

        if flight_seat.status != FlightSeat.Status.AVAILABLE:
            raise serializers.ValidationError(f"Seat {flight_seat} is not available.")
        
def validate_passenger_name(value, field_name):
    value = value.strip()

    if not value:
        raise serializers.ValidationError(f"{field_name} cannot be empty.")

    return value