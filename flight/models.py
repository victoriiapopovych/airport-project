from django.db import models
from location.models import Airport
from airline.models import Airline, Airplane, AirplaneSeat
from django.conf import settings

# Create your models here.
class Route(models.Model):
    departure_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="departure_routes")
    arrival_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="arrival_routes")
    distance_km = models.PositiveIntegerField()
    estimated_duration = models.DurationField()

    def __str__(self):
        return f"{self.departure_airport.name} → {self.arrival_airport.name}"
    

class Flight(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        DELAYED = "delayed", "Delayed"
        BOARDING = "boarding", "Boarding"
        DEPARTED = "departed", "Departed"
        ARRIVED = "arrived", "Arrived"
        CANCELLED = "cancelled", "Cancelled"

    flight_number = models.CharField(max_length=20, unique=True)
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="flights")
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE, related_name="flights")
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE, related_name="flights")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    terminal_name = models.CharField(max_length=10, blank=True)
    boarding_gate = models.CharField(max_length=10, blank=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.flight_number}: {self.route}"
    
    class Meta:
        ordering = ("departure_time",)


class FlightSeat(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        HELD = "held", "Held"
        SOLD = "sold", "Sold"
        BLOCKED = "blocked", "Blocked"

    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="seats")
    airplane_seat = models.ForeignKey(AirplaneSeat, on_delete=models.CASCADE, related_name="flight_seats")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)

    held_until = models.DateTimeField(null=True, blank=True)
    held_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="held_flight_seats")

    class Meta:
        unique_together = ("flight", "airplane_seat")

    def __str__(self):
        return f"{self.flight.flight_number} - {self.airplane_seat}"