from ticket.models import Ticket


def get_user_tickets(user_id: int, status=None, flight_number=None, limit=10):
    tickets = (
        Ticket.objects
        .filter(booking__user_id=user_id)
        .select_related(
            "booking",
            "flight",
            "airplane_seat",
            "airplane_seat__seat_class",
        )
    )

    if status:
        tickets = tickets.filter(status__iexact=status)

    if flight_number:
        tickets = tickets.filter(flight__flight_number__iexact=flight_number)

    tickets = tickets.order_by("-booking__created_at")[:limit]

    result = []

    for ticket in tickets:
        result.append({
            "ticket_id": ticket.id,
            "booking_id": ticket.booking_id,
            "flight_number": ticket.flight.flight_number,
            "seat_number": ticket.airplane_seat.seat_number,
            "seat_class": ticket.airplane_seat.seat_class.class_type,
            "passenger_first_name": ticket.passenger_first_name,
            "passenger_last_name": ticket.passenger_last_name,
            "price": str(ticket.price),
            "status": ticket.status,
            "booking_status": ticket.booking.status,
        })

    return result


def get_ticket_details(user_id: int, ticket_id: int):
    if not ticket_id:
        return {"error": "ticket_id is required."}

    ticket = (
        Ticket.objects
        .filter(
            id=ticket_id,
            booking__user_id=user_id,
        )
        .select_related(
            "booking",
            "flight",
            "flight__airline",
            "flight__route__departure_airport",
            "flight__route__arrival_airport",
            "airplane_seat",
            "airplane_seat__seat_class",
        )
        .first()
    )

    if not ticket:
        return {
            "error": f"Ticket {ticket_id} was not found for this user."
        }

    flight = ticket.flight
    seat = ticket.airplane_seat

    return {
        "ticket_id": ticket.id,
        "booking_id": ticket.booking_id,
        "ticket_status": ticket.status,
        "booking_status": ticket.booking.status,
        "passenger_first_name": ticket.passenger_first_name,
        "passenger_last_name": ticket.passenger_last_name,
        "price": str(ticket.price),

        "flight": {
            "flight_number": flight.flight_number,
            "airline": flight.airline.name,
            "from": flight.route.departure_airport.name,
            "to": flight.route.arrival_airport.name,
            "departure_time": flight.departure_time.isoformat(),
            "arrival_time": flight.arrival_time.isoformat(),
            "status": flight.status,
            "terminal": flight.terminal_name,
            "gate": flight.boarding_gate,
        },

        "seat": {
            "seat_number": seat.seat_number,
            "seat_class": seat.seat_class.class_type,
            "is_window": seat.is_window,
            "is_aisle": seat.is_aisle,
            "is_exit_row": seat.is_exit_row,
            "has_extra_legroom": seat.has_extra_legroom,
        },
    }