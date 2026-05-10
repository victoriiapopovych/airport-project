from django.contrib import admin
from .models import Country, City, Airport

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "country")
    search_fields = ("name",)
    list_filter = ("country",)

@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")
    list_filter = ("city",)
