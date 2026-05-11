from django.contrib import admin
from .models import Airline, AirplaneType, Airplane

# Register your models here.
@admin.register(Airline)
class AirlineAdmin(admin.ModelAdmin):
    list_display = ("name", "iata_code", "country", "is_active")
    list_filter = ("country", "is_active")
    search_fields = ("name", "iata_code")

@admin.register(AirplaneType)
class AirplaneTypeAdmin(admin.ModelAdmin):
    list_display = (
        "manufacturer",
        "code",
    )

    search_fields = (
        "manufacturer",
        "code",
    )

@admin.register(Airplane)
class AirplaneAdmin(admin.ModelAdmin):
    list_display = (
        "tail_number",
        "airline",
        "airplane_type",
        "num_of_passengers",
        "crew_count",
        "is_active",
    )

    list_filter = (
        "airline",
        "is_active",
    )

    search_fields = (
        "tail_number",
    )
