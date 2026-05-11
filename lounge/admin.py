from django.contrib import admin
from .models import Lounge, LoungeAccess

# Register your models here.
@admin.register(Lounge)
class LoungeAdmin(admin.ModelAdmin):
    list_display = ("name", "airport", "capacity", "opening_time", "closing_time", "is_active")
    list_filter = ("airport", "is_active")
    search_fields = ("name", "airport__name")


@admin.register(LoungeAccess)
class LoungeAccessAdmin(admin.ModelAdmin):
    list_display = ("user", "lounge", "ticket", "access_type", "valid_from", "valid_until", "is_used")
    list_filter = ("access_type", "is_used", "lounge")
    search_fields = ("user__username", "lounge__name")
