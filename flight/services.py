from ticket.models import Ticket


def calculate_ticket_price(flight, airplane_seat):
    return flight.base_price + airplane_seat.seat_class.extra_price


def get_taken_seat_ids_for_flight(flight):
    return Ticket.objects.filter(
        flight=flight,
        status__in=[
            Ticket.Status.PENDING,
            Ticket.Status.PAID,
        ],
    ).values_list("airplane_seat_id", flat=True)


def get_available_seats_for_flight(flight):
    taken_seat_ids = get_taken_seat_ids_for_flight(flight)

    return flight.airplane.seats.filter(
        is_active=True,
    ).exclude(
        id__in=taken_seat_ids,
    ).select_related("seat_class")


def get_available_seats_count_for_flight(flight):
    return get_available_seats_for_flight(flight).count()