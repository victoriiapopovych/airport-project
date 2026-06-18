from airline.models import Airline


def get_airlines(country_name=None, limit=10):
    airlines = Airline.objects.select_related("country").filter(is_active=True)

    if country_name:
        airlines = airlines.filter(country__name__icontains=country_name)

    airlines = airlines.order_by("name")[:limit]

    return [
        {
            "airline_id": airline.id,
            "name": airline.name,
            "iata_code": airline.iata_code,
            "country": airline.country.name,
            "is_active": airline.is_active,
        }
        for airline in airlines
    ]


def get_airline_details(airline_id=None, airline_name=None):
    if not airline_id and not airline_name:
        return {"error": "airline_id or airline_name is required."}

    airlines = Airline.objects.select_related("country").prefetch_related("airports")

    if airline_id:
        airline = airlines.filter(id=airline_id).first()
    else:
        airline = airlines.filter(name__icontains=airline_name).first()

    if not airline:
        return {"error": "Airline was not found."}

    return {
        "airline_id": airline.id,
        "name": airline.name,
        "iata_code": airline.iata_code,
        "country": airline.country.name,
        "is_active": airline.is_active,
        "airports": [
            {
                "airport_id": airport.id,
                "name": airport.name,
                "code": airport.code,
            }
            for airport in airline.airports.all()
        ],
    }