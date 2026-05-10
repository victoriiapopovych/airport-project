from django.contrib import admin
from .models import TicketClass, Booking, Ticket

# Register your models here.
@admin.register(TicketClass)
class TicketClassAdmin(admin.ModelAdmin):
    list_display = ("class_type", "baggage_kg", "priority_boarding", "lounge_access")
    list_filter = ("priority_boarding", "lounge_access")
    search_fields = ("class_type",)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at", "status", "total_price")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "user__email")


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("passenger_first_name", "passenger_last_name", "flight", "ticket_class", "seat_number", "price", "status")
    list_filter = ("status", "ticket_class")
    search_fields = ("passenger_first_name", "passenger_last_name", "seat_number", "flight__flight_number")