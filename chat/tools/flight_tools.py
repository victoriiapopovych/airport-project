from datetime import datetime

from django.utils import timezone

from flight.models import Flight


def get_available_flights(
    departure_city=None,
    arrival_city=None,
    departure_airport=None,
    arrival_airport=None,
    airline=None,
    flight_date=None,
    status=None,
    limit=10,
):
    flights = (
        Flight.objects
        .select_related(
            "route__departure_airport",
            "route__departure_airport__city",
            "route__arrival_airport",
            "route__arrival_airport__city",
            "airline",
        )
        .filter(
            departure_time__gte=timezone.now(),
        )
    )

    if status:
        flights = flights.filter(status__iexact=status)
    else:
        flights = flights.filter(
            status__in=[
                Flight.Status.SCHEDULED,
                Flight.Status.DELAYED,
                Flight.Status.BOARDING,
            ],
        )

    if departure_city:
        flights = flights.filter(
            route__departure_airport__city__name__icontains=departure_city
        )

    if arrival_city:
        flights = flights.filter(
            route__arrival_airport__city__name__icontains=arrival_city
        )

    if departure_airport:
        flights = flights.filter(
            route__departure_airport__name__icontains=departure_airport
        )

    if arrival_airport:
        flights = flights.filter(
            route__arrival_airport__name__icontains=arrival_airport
        )

    if airline:
        flights = flights.filter(
            airline__name__icontains=airline
        )

    if flight_date:
        parsed_date = _parse_date(flight_date)

        if parsed_date:
            flights = flights.filter(
                departure_time__date=parsed_date
            )

    flights = flights.order_by("departure_time")[:limit]

    result = []

    for flight in flights:
        result.append({
            "flight_number": flight.flight_number,
            "airline": flight.airline.name,
            "from_airport": flight.route.departure_airport.name,
            "from_city": flight.route.departure_airport.city.name,
            "to_airport": flight.route.arrival_airport.name,
            "to_city": flight.route.arrival_airport.city.name,
            "departure_time": flight.departure_time.isoformat(),
            "arrival_time": flight.arrival_time.isoformat(),
            "status": flight.status,
            "terminal": flight.terminal_name,
            "gate": flight.boarding_gate,
            "base_price": str(flight.base_price),
        })

    return result


def get_flight_details(flight_number: str):
    if not flight_number:
        return {
            "error": "flight_number is required."
        }

    flight = (
        Flight.objects
        .select_related(
            "route__departure_airport",
            "route__departure_airport__city",
            "route__arrival_airport",
            "route__arrival_airport__city",
            "airline",
            "airplane",
        )
        .filter(flight_number__iexact=flight_number)
        .first()
    )

    if not flight:
        return {
            "error": f"Flight {flight_number} was not found."
        }

    return {
        "flight_number": flight.flight_number,
        "airline": flight.airline.name,
        "from_airport": flight.route.departure_airport.name,
        "from_city": flight.route.departure_airport.city.name,
        "to_airport": flight.route.arrival_airport.name,
        "to_city": flight.route.arrival_airport.city.name,
        "departure_time": flight.departure_time.isoformat(),
        "arrival_time": flight.arrival_time.isoformat(),
        "status": flight.status,
        "terminal": flight.terminal_name,
        "gate": flight.boarding_gate,
        "base_price": str(flight.base_price),
        "airplane": flight.airplane.tail_number if flight.airplane else None,
    }


def _parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None