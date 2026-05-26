from django.db import models
from location.models import Country, Airport

# Create your models here.
class Airline(models.Model):
    name = models.CharField(max_length=100, unique=True)
    iata_code = models.CharField(max_length=3, unique=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="airlines")
    is_active = models.BooleanField(default=True)
    airports = models.ManyToManyField(Airport, related_name="airlines")

    def __str__(self):
        return f"{self.name} ({self.iata_code})"

class AirplaneType(models.Model):
    manufacturer = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return f"{self.manufacturer} {self.code}"

class Airplane(models.Model):
    tail_number = models.CharField(max_length=15, unique=True)
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE, related_name="airplanes")
    airplane_type = models.ForeignKey(AirplaneType, on_delete=models.CASCADE, related_name="airplanes")
    manufactured_year = models.PositiveIntegerField()
    num_of_passengers = models.PositiveIntegerField()
    crew_count = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.tail_number} ({self.airplane_type})"

class SeatClass(models.Model):
    class Type(models.TextChoices):
        ECONOMY = "economy", "Economy"
        PREMIUM_ECONOMY = "premium_economy", "Premium Economy"
        BUSINESS = "business", "Business"
        FIRST = "first", "First"

    airline = models.ForeignKey(Airline, on_delete=models.CASCADE, related_name="seat_classes")
    class_type = models.CharField(max_length=30, choices=Type.choices)
    extra_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    baggage_kg = models.PositiveIntegerField(default=0)
    priority_boarding = models.BooleanField(default=False)
    lounge_access = models.BooleanField(default=False)

    class Meta:
        unique_together = ("airline", "class_type")

    def __str__(self):
        return f"{self.airline.name} - {self.get_class_type_display()}"
    
class AirplaneSeat(models.Model):
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE, related_name="seats")
    seat_class = models.ForeignKey(SeatClass, on_delete=models.PROTECT, related_name="airplane_seats")

    row_number = models.PositiveIntegerField()
    seat_letter = models.CharField(max_length=1)

    is_window = models.BooleanField(default=False)
    is_aisle = models.BooleanField(default=False)
    is_exit_row = models.BooleanField(default=False)
    has_extra_legroom = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("airplane", "row_number", "seat_letter")

    def __str__(self):
        return f"{self.row_number}{self.seat_letter} - {self.airplane}"