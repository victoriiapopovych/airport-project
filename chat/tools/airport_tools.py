from location.models import Airport


def get_airports(city_name=None, country_name=None, limit=10):
    airports = Airport.objects.select_related("city", "city__country")

    if city_name:
        airports = airports.filter(city__name__icontains=city_name)

    if country_name:
        airports = airports.filter(city__country__name__icontains=country_name)

    airports = airports.order_by("name")[:limit]

    return [
        {
            "airport_id": airport.id,
            "name": airport.name,
            "code": airport.code,
            "city": airport.city.name,
            "country": airport.city.country.name,
        }
        for airport in airports
    ]


def get_airport_details(airport_id: int):
    if not airport_id:
        return {"error": "airport_id is required."}

    airport = (
        Airport.objects
        .select_related("city", "city__country")
        .filter(id=airport_id)
        .first()
    )

    if not airport:
        return {"error": f"Airport {airport_id} was not found."}

    return {
        "airport_id": airport.id,
        "name": airport.name,
        "code": airport.code,
        "city": airport.city.name,
        "country": airport.city.country.name,
    }