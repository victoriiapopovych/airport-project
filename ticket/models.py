from django.db import models
from django.conf import settings
from flight.models import Flight

class TicketClass(models.Model):

    class ClassType(models.TextChoices):
        ECONOMY = "economy", "Economy"
        BUSINESS = "business", "Business"
        FIRST = "first", "First Class"

    class_type = models.CharField(max_length=20, choices=ClassType.choices, unique=True)
    baggage_kg = models.PositiveIntegerField()
    priority_boarding = models.BooleanField(default=False)
    lounge_access = models.BooleanField(default=False)
    extra_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.get_class_type_display()
    

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
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="tickets")
    ticket_class = models.ForeignKey(TicketClass, on_delete=models.PROTECT, related_name="tickets")
    passenger_first_name = models.CharField(max_length=100)
    passenger_last_name = models.CharField(max_length=100)
    seat_number = models.CharField(max_length=10, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.BOOKED)

    def __str__(self):
        return f"{self.passenger_first_name} {self.passenger_last_name} - {self.flight}"
    

