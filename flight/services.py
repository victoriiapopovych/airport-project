
def build_seat_number(flight_seat):
    return (
        f"{flight_seat.airplane_seat.row_number}"
        f"{flight_seat.airplane_seat.seat_letter}"
    )


def calculate_ticket_price(flight_seat):
    base_price = flight_seat.flight.base_price
    extra_price = flight_seat.airplane_seat.seat_class.extra_price

    return base_price + extra_price