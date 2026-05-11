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
