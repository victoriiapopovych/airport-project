import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Flight, FlightSeat


logger = logging.getLogger(__name__)


@receiver(post_save, sender=Flight)
def create_flight_seats(sender, instance, created, **kwargs):
    if not created:
        logger.debug(
            "Flight %s was updated. Flight seats generation skipped.",
            instance.flight_number,
        )
        return

    airplane_seats = instance.airplane.seats.filter(is_active=True)

    if not airplane_seats.exists():
        logger.warning(
            "Flight seats were not created for flight %s because airplane %s has no active seats.",
            instance.flight_number,
            instance.airplane.tail_number,
        )
        return

    flight_seats = [
        FlightSeat(
            flight=instance,
            airplane_seat=airplane_seat,
            status=FlightSeat.Status.AVAILABLE,
        )
        for airplane_seat in airplane_seats
    ]

    FlightSeat.objects.bulk_create(flight_seats, ignore_conflicts=True)

    logger.info(
        "Created %s flight seats for flight %s using airplane %s.",
        len(flight_seats),
        instance.flight_number,
        instance.airplane.tail_number,
    )