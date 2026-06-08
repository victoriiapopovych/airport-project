from django.contrib import admin

from .models import Booking, Ticket


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at", "status", "total_price")
    list_filter = ("status", "created_at")
    search_fields = ("user__email", "user__first_name", "user__last_name")


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "booking",
        "flight",
        "airplane_seat",
        "passenger_first_name",
        "passenger_last_name",
        "price",
        "status",
    )
    list_filter = ("status", "flight")
    search_fields = (
        "passenger_first_name",
        "passenger_last_name",
        "booking__user__email",
        "flight__flight_number",
    )