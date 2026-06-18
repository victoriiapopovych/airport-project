from airline.models import AirplaneSeat
from flight.models import Flight
from ticket.models import Ticket


ACTIVE_TICKET_STATUSES = [
    Ticket.Status.PENDING,
    Ticket.Status.PAID,
]


def get_available_seats(flight_number: str, seat_class=None, limit=30):
    if not flight_number:
        return {"error": "flight_number is required."}

    flight = (
        Flight.objects
        .select_related("airplane")
        .filter(flight_number__iexact=flight_number)
        .first()
    )

    if not flight:
        return {"error": f"Flight {flight_number} was not found."}

    occupied_seat_ids = Ticket.objects.filter(
        flight=flight,
        status__in=ACTIVE_TICKET_STATUSES,
    ).values_list("airplane_seat_id", flat=True)

    seats = (
        AirplaneSeat.objects
        .select_related("seat_class")
        .filter(
            airplane=flight.airplane,
            is_active=True,
        )
        .exclude(id__in=occupied_seat_ids)
    )

    if seat_class:
        seats = seats.filter(
            seat_class__class_type__iexact=seat_class
        )

    seats = seats.order_by(
        "row_number",
        "seat_letter",
    )[:limit]

    result = []

    for seat in seats:
        result.append({
            "seat_number": seat.seat_number,
            "seat_class": seat.seat_class.class_type,
            "price": str(flight.base_price + seat.seat_class.extra_price),
            "is_window": seat.is_window,
            "is_aisle": seat.is_aisle,
            "is_exit_row": seat.is_exit_row,
            "has_extra_legroom": seat.has_extra_legroom,
        })

    return result


def get_seat_details(flight_number: str, seat_number: str):
    if not flight_number:
        return {"error": "flight_number is required."}

    if not seat_number:
        return {"error": "seat_number is required."}

    row_number, seat_letter = _parse_seat_number(seat_number)

    if not row_number or not seat_letter:
        return {
            "error": "Invalid seat number format. Example: 1A, 12C."
        }

    flight = (
        Flight.objects
        .select_related("airplane")
        .filter(flight_number__iexact=flight_number)
        .first()
    )

    if not flight:
        return {"error": f"Flight {flight_number} was not found."}

    seat = (
        AirplaneSeat.objects
        .select_related("seat_class")
        .filter(
            airplane=flight.airplane,
            row_number=row_number,
            seat_letter__iexact=seat_letter,
        )
        .first()
    )

    if not seat:
        return {
            "error": f"Seat {seat_number} was not found for flight {flight_number}."
        }

    active_ticket = Ticket.objects.filter(
        flight=flight,
        airplane_seat=seat,
        status__in=ACTIVE_TICKET_STATUSES,
    ).first()

    is_available = active_ticket is None

    return {
        "flight_number": flight.flight_number,
        "seat_number": seat.seat_number,
        "seat_class": seat.seat_class.class_type,
        "price": str(flight.base_price + seat.seat_class.extra_price),
        "is_available": is_available,
        "ticket_status": active_ticket.status if active_ticket else None,
        "is_window": seat.is_window,
        "is_aisle": seat.is_aisle,
        "is_exit_row": seat.is_exit_row,
        "has_extra_legroom": seat.has_extra_legroom,
    }


def _parse_seat_number(seat_number: str):
    seat_number = seat_number.strip().upper()

    row_part = ""
    letter_part = ""

    for char in seat_number:
        if char.isdigit():
            row_part += char
        elif char.isalpha():
            letter_part += char

    if not row_part or not letter_part:
        return None, None

    return int(row_part), letter_part