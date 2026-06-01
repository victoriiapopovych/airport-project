from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Flight, FlightSeat


@receiver(post_save, sender=Flight)
def create_flight_seats(sender, instance, created, **kwargs):
    if not created:
        return

    airplane_seats = instance.airplane.seats.filter(is_active=True)

    flight_seats = [
        FlightSeat(
            flight=instance,
            airplane_seat=airplane_seat,
            status=FlightSeat.Status.AVAILABLE
        )
        for airplane_seat in airplane_seats
    ]

    FlightSeat.objects.bulk_create(flight_seats, ignore_conflicts=True)