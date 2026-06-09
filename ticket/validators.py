from rest_framework import serializers
from django.utils import timezone

from .models import Ticket


MAX_TICKETS_PER_BOOKING = 10


def validate_ticket_limit(tickets):
    if not tickets:
        raise serializers.ValidationError("At least one ticket is required.")

    if len(tickets) > MAX_TICKETS_PER_BOOKING:
        raise serializers.ValidationError(
            f"You can book maximum {MAX_TICKETS_PER_BOOKING} tickets at once."
        )


def validate_duplicate_seats(tickets):
    seat_pairs = [
        (item["flight"].id, item["airplane_seat"].id)
        for item in tickets
    ]

    if len(seat_pairs) != len(set(seat_pairs)):
        raise serializers.ValidationError("You cannot book the same seat twice.")


def validate_same_flight(tickets):
    flight_ids = {item["flight"].id for item in tickets}

    if len(flight_ids) > 1:
        raise serializers.ValidationError(
            "All tickets in one booking must belong to the same flight."
        )


def validate_seats_belong_to_flight_airplane(tickets):
    for item in tickets:
        flight = item["flight"]
        airplane_seat = item["airplane_seat"]

        if airplane_seat.airplane_id != flight.airplane_id:
            raise serializers.ValidationError(
                f"Seat {airplane_seat.seat_number} does not belong to airplane "
                f"{flight.airplane.tail_number}."
            )


def validate_flight_status(flight):
    if flight.status in [
        flight.Status.CANCELLED,
        flight.Status.DEPARTED,
        flight.Status.ARRIVED,
    ]:
        raise serializers.ValidationError(
            f"Flight {flight.flight_number} is not available for booking."
        )


def validate_flight_departure(flight):
    if flight.departure_time <= timezone.now():
        raise serializers.ValidationError(
            f"Flight {flight.flight_number} has already departed."
        )


def validate_available_seats(tickets):
    for item in tickets:
        flight = item["flight"]
        airplane_seat = item["airplane_seat"]

        exists = Ticket.objects.filter(
            flight=flight,
            airplane_seat=airplane_seat,
            status__in=[
                Ticket.Status.PENDING,
                Ticket.Status.PAID,
            ],
        ).exists()

        if exists:
            raise serializers.ValidationError(
                f"Seat {airplane_seat.seat_number} is not available."
            )


def validate_passenger_name(value, field_name):
    value = value.strip()

    if not value:
        raise serializers.ValidationError(f"{field_name} cannot be empty.")

    return value