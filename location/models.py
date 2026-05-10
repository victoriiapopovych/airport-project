from django.db import models

# Create your models here.
class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=3, unique=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

class City(models.Model):
    name = models.CharField(max_length=50)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="cities")

    def __str__(self):
        return self.name
    
class Airport(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="airports")

    def __str__(self):
        return f"{self.name} ({self.code})"