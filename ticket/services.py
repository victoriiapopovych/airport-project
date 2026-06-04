import logging

from django.utils import timezone
from rest_framework import serializers

from .models import Booking, Ticket
from flight.models import FlightSeat


logger = logging.getLogger(__name__)


def expire_booking(booking):
    if booking.status != Booking.Status.PENDING:
        logger.debug(
            "Booking %s expiration skipped because status is %s.",
            booking.id,
            booking.status,
        )
        return

    expired_seats = booking.tickets.filter(
        flight_seat__status=FlightSeat.Status.PENDING,
        flight_seat__pending_until__lt=timezone.now(),
    )

    if not expired_seats.exists():
        logger.debug(
            "Booking %s expiration skipped because there are no expired seats.",
            booking.id,
        )
        return

    booking.status = Booking.Status.EXPIRED
    booking.save()

    cancelled_tickets_count = 0

    for ticket in booking.tickets.all():
        ticket.status = Ticket.Status.CANCELLED
        ticket.save()

        flight_seat = ticket.flight_seat
        flight_seat.status = FlightSeat.Status.AVAILABLE
        flight_seat.pending_until = None
        flight_seat.pending_by = None
        flight_seat.save()

        cancelled_tickets_count += 1

    logger.info(
        "Booking %s expired. Cancelled %s tickets and released related flight seats.",
        booking.id,
        cancelled_tickets_count,
    )


def cancel_booking(booking):
    logger.info(
        "Cancelling booking %s for user %s.",
        booking.id,
        booking.user_id,
    )

    booking.status = Booking.Status.CANCELLED
    booking.save()

    cancelled_tickets_count = 0
    released_seats_count = 0

    for ticket in booking.tickets.all():
        ticket.status = Ticket.Status.CANCELLED
        ticket.save()
        cancelled_tickets_count += 1

        flight_seat = ticket.flight_seat

        if flight_seat.status == FlightSeat.Status.PENDING:
            flight_seat.status = FlightSeat.Status.AVAILABLE
            flight_seat.pending_until = None
            flight_seat.pending_by = None
            flight_seat.save()
            released_seats_count += 1

    logger.info(
        "Booking %s cancelled. Cancelled %s tickets and released %s flight seats.",
        booking.id,
        cancelled_tickets_count,
        released_seats_count,
    )


def create_booking(user, tickets_data):
    logger.info(
        "Creating booking for user %s with %s tickets.",
        user.id,
        len(tickets_data),
    )

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
            logger.warning(
                "Booking %s creation failed for user %s: flight seat %s is not available.",
                booking.id,
                user.id,
                flight_seat.id,
            )
            raise serializers.ValidationError(f"Seat {flight_seat} is not available.")

        seat_class = flight_seat.airplane_seat.seat_class
        price = flight_seat.flight.base_price + seat_class.extra_price

        ticket = Ticket.objects.create(
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

        logger.info(
            "Ticket %s created for booking %s. Flight seat %s set to pending until %s.",
            ticket.id,
            booking.id,
            flight_seat.id,
            flight_seat.pending_until,
        )

    booking.total_price = total_price
    booking.save()

    logger.info(
        "Booking %s created successfully for user %s. Total price: %s.",
        booking.id,
        user.id,
        booking.total_price,
    )

    return booking