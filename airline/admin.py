from django.contrib import admin
from .models import Airline, AirplaneType, Airplane, SeatClass, AirplaneSeat

# Register your models here.
@admin.register(Airline)
class AirlineAdmin(admin.ModelAdmin):
    list_display = ("name", "iata_code", "country", "is_active")
    list_filter = ("country", "is_active")
    search_fields = ("name", "iata_code")

@admin.register(AirplaneType)
class AirplaneTypeAdmin(admin.ModelAdmin):
    list_display = ("manufacturer","code")
    search_fields = ("manufacturer","code")

@admin.register(Airplane)
class AirplaneAdmin(admin.ModelAdmin):
    list_display = ("tail_number","airline","airplane_type","num_of_passengers","crew_count","is_active")
    list_filter = ("airline","is_active")
    search_fields = ("tail_number",)

@admin.register(SeatClass)
class SeatClassAdmin(admin.ModelAdmin):
    list_display = ("airline", "class_type", "extra_price", "baggage_kg", "priority_boarding", "lounge_access")
    list_filter = ("airline", "class_type", "priority_boarding", "lounge_access")
    search_fields = ("airline__name", "class_type")


@admin.register(AirplaneSeat)
class AirplaneSeatAdmin(admin.ModelAdmin):
    list_display = ("airplane", "row_number", "seat_letter", "seat_class", "is_window", "is_aisle", "is_exit_row", "has_extra_legroom", "is_active")
    list_filter = ("airplane", "seat_class", "is_window", "is_aisle", "is_exit_row", "has_extra_legroom", "is_active")
    search_fields = ("airplane__tail_number", "seat_letter")
