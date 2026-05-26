from django.db import models
from django.conf import settings
from flight.models import FlightSeat


class Booking(models.Model):

    class Status(models.TextChoices):
        CREATED = "created", "Created"
        PAID = "paid", "Paid"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CREATED)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Booking #{self.id} - {self.user}"
    
class Ticket(models.Model):

    class Status(models.TextChoices):
        BOOKED = "booked", "Booked"
        PAID = "paid", "Paid"
        USED = "used", "Used"
        CANCELLED = "cancelled", "Cancelled"

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="tickets")
    flight_seat = models.ForeignKey(FlightSeat, on_delete=models.PROTECT, related_name="tickets")
    passenger_first_name = models.CharField(max_length=100)
    passenger_last_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.BOOKED)

    def __str__(self):
        return f"{self.passenger_first_name} {self.passenger_last_name} - {self.flight_seat}"
    

