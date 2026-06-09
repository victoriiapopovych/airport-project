import logging
from decimal import Decimal

from django.db import IntegrityError, transaction
from rest_framework import serializers

from .models import Booking, Ticket

logger = logging.getLogger(__name__)

from datetime import timedelta
from django.utils import timezone


def calculate_ticket_price(flight, airplane_seat):
    return flight.base_price + airplane_seat.seat_class.extra_price


def cancel_booking(booking):
    logger.info(
        "Cancelling booking %s for user %s.",
        booking.id,
        booking.user_id,
    )

    booking.status = Booking.Status.CANCELLED
    booking.save(update_fields=["status"])

    cancelled_tickets_count = booking.tickets.exclude(
        status=Ticket.Status.CANCELLED
    ).update(status=Ticket.Status.CANCELLED)

    logger.info(
        "Booking %s cancelled. Cancelled %s tickets.",
        booking.id,
        cancelled_tickets_count,
    )


@transaction.atomic
def create_booking(user, tickets_data):
    logger.info(
        "Creating booking for user %s with %s tickets.",
        user.id,
        len(tickets_data),
    )

    booking = Booking.objects.create(
        user=user,
        status=Booking.Status.PENDING,
        total_price=Decimal("0.00")
    )

    total_price = Decimal("0.00")
    tickets_to_create = []

    for item in tickets_data:
        flight = item["flight"]
        airplane_seat = item["airplane_seat"]

        price = calculate_ticket_price(flight, airplane_seat)
        total_price += price

        tickets_to_create.append(
            Ticket(
                booking=booking,
                flight=flight,
                airplane_seat=airplane_seat,
                passenger_first_name=item["passenger_first_name"],
                passenger_last_name=item["passenger_last_name"],
                price=price,
                status=Ticket.Status.PENDING,
            )
        )

    try:
        Ticket.objects.bulk_create(tickets_to_create)
    except IntegrityError:
        raise serializers.ValidationError("One of the selected seats is already booked.")

    booking.total_price = total_price
    booking.save(update_fields=["total_price"])

    logger.info(
        "Booking %s created successfully for user %s. Total price: %s.",
        booking.id,
        user.id,
        booking.total_price,
    )

    return booking