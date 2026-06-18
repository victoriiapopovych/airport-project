from ticket.models import Booking


def get_user_bookings(user_id: int, status=None, limit=10):
    bookings = (
        Booking.objects
        .filter(user_id=user_id)
        .prefetch_related(
            "tickets",
            "tickets__flight",
            "tickets__airplane_seat",
        )
    )

    if status:
        bookings = bookings.filter(status__iexact=status)

    bookings = bookings.order_by("-created_at")[:limit]

    result = []

    for booking in bookings:
        result.append({
            "booking_id": booking.id,
            "status": booking.status,
            "total_price": str(booking.total_price),
            "created_at": booking.created_at.isoformat(),
            "tickets_count": booking.tickets.count(),
        })

    return result


def get_booking_details(user_id: int, booking_id: int):
    if not booking_id:
        return {"error": "booking_id is required."}

    booking = (
        Booking.objects
        .filter(id=booking_id, user_id=user_id)
        .prefetch_related(
            "tickets",
            "tickets__flight",
            "tickets__airplane_seat",
            "tickets__airplane_seat__seat_class",
        )
        .first()
    )

    if not booking:
        return {
            "error": f"Booking {booking_id} was not found for this user."
        }

    tickets = []

    for ticket in booking.tickets.all():
        tickets.append({
            "ticket_id": ticket.id,
            "flight_number": ticket.flight.flight_number,
            "seat_number": ticket.airplane_seat.seat_number,
            "seat_class": ticket.airplane_seat.seat_class.class_type,
            "passenger_first_name": ticket.passenger_first_name,
            "passenger_last_name": ticket.passenger_last_name,
            "price": str(ticket.price),
            "status": ticket.status,
        })

    return {
        "booking_id": booking.id,
        "status": booking.status,
        "total_price": str(booking.total_price),
        "created_at": booking.created_at.isoformat(),
        "tickets": tickets,
    }