from django.contrib import admin
from .models import Lounge, LoungeAccess


@admin.register(Lounge)
class LoungeAdmin(admin.ModelAdmin):
    list_display = ("name", "airport", "capacity", "access_price", "opening_time", "closing_time", "is_active")
    list_filter = ("airport", "is_active")
    search_fields = ("name", "airport__name")


@admin.register(LoungeAccess)
class LoungeAccessAdmin(admin.ModelAdmin):
    list_display = ("user", "lounge", "ticket", "access_type", "price", "is_paid", "paid_at", "valid_from", "valid_until", "is_used", "status")
    list_filter = ("access_type", "is_paid", "is_used", "status", "lounge")
    search_fields = ("user__email", "user__first_name", "user__last_name", "lounge__name")