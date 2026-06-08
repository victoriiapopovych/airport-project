from django.conf import settings
from django.db import models

from airline.models import AirplaneSeat
from flight.models import Flight


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        CANCELLED = "cancelled", "Cancelled"
        EXPIRED = "expired", "Expired"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Booking #{self.id} - {self.user}"


class Ticket(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        USED = "used", "Used"
        CANCELLED = "cancelled", "Cancelled"

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="tickets")
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="tickets")
    airplane_seat = models.ForeignKey(AirplaneSeat, on_delete=models.PROTECT, related_name="tickets")
    passenger_first_name = models.CharField(max_length=100)
    passenger_last_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["flight", "airplane_seat"],
                condition=models.Q(status__in=["pending", "paid"]),
                name="unique_active_ticket_per_flight_seat",
            )
        ]

    def __str__(self):
        return (
            f"{self.passenger_first_name} {self.passenger_last_name} - "
            f"{self.flight.flight_number} - {self.airplane_seat.seat_number}"
        )