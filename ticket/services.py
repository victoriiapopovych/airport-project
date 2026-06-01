from django.utils import timezone

from .models import Booking, Ticket
from flight.models import FlightSeat

from rest_framework import serializers


def expire_booking(booking):
    if booking.status != Booking.Status.PENDING:
        return

    expired_seats = booking.tickets.filter(
        flight_seat__status=FlightSeat.Status.PENDING,
        flight_seat__pending_until__lt=timezone.now(),
    )

    if not expired_seats.exists():
        return

    booking.status = Booking.Status.EXPIRED
    booking.save()

    for ticket in booking.tickets.all():
        ticket.status = Ticket.Status.CANCELLED
        ticket.save()

        flight_seat = ticket.flight_seat
        flight_seat.status = FlightSeat.Status.AVAILABLE
        flight_seat.pending_until = None
        flight_seat.pending_by = None
        flight_seat.save()


def cancel_booking(booking):
    booking.status = Booking.Status.CANCELLED
    booking.save()

    for ticket in booking.tickets.all():
        ticket.status = Ticket.Status.CANCELLED
        ticket.save()

        flight_seat = ticket.flight_seat

        if flight_seat.status == FlightSeat.Status.PENDING:
            flight_seat.status = FlightSeat.Status.AVAILABLE
            flight_seat.pending_until = None
            flight_seat.pending_by = None
            flight_seat.save()


def create_booking(user, tickets_data):
    booking = Booking.objects.create(
        user=user,
        status=Booking.Status.PENDING,
    )

    total_price = 0

    for item in tickets_data:
        flight_seat = FlightSeat.objects.select_for_update().get(
            id=item["flight_seat"].id
        )

        if flight_seat.status != FlightSeat.Status.AVAILABLE:
            raise serializers.ValidationError(f"Seat {flight_seat} is not available.")

        seat_class = flight_seat.airplane_seat.seat_class

        price = flight_seat.flight.base_price + seat_class.extra_price

        Ticket.objects.create(
            booking=booking,
            flight_seat=flight_seat,
            passenger_first_name=item["passenger_first_name"],
            passenger_last_name=item["passenger_last_name"],
            price=price,
            status=Ticket.Status.PENDING,
        )

        flight_seat.status = FlightSeat.Status.PENDING
        flight_seat.pending_until = timezone.now() + timezone.timedelta(minutes=15)
        flight_seat.pending_by = user
        flight_seat.save()

        total_price += price

    booking.total_price = total_price
    booking.save()

    return booking