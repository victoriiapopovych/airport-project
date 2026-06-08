from django.db import transaction

from .models import AirplaneSeat, SeatClass

import logging
logger = logging.getLogger(__name__)


DEFAULT_SEAT_LETTERS = ["A", "B", "C", "D", "E", "F"]


def generate_airplane_seats(
    airplane,
    rows=30,
    letters=None,
    class_rows=None,
    exit_rows=None,
    window_letters=None,
    aisle_letters=None,
):
    logger.info(
        "Starting seats generation for airplane %s.",
        airplane.tail_number,
    )

    if letters is None:
        letters = DEFAULT_SEAT_LETTERS

    if class_rows is None:
        class_rows = {}

    if exit_rows is None:
        exit_rows = []

    rows = int(rows)

    if rows <= 0:
        raise ValueError("Rows count must be greater than 0.")

    letters = [str(letter).strip().upper() for letter in letters]

    if not letters:
        raise ValueError("Seat letters cannot be empty.")

    if any(not letter for letter in letters):
        raise ValueError("Seat letters cannot contain empty values.")

    if len(letters) != len(set(letters)):
        raise ValueError("Seat letters must be unique.")

    if window_letters is None:
        window_letters = [letters[0], letters[-1]]
    else:
        window_letters = [
            str(letter).strip().upper()
            for letter in window_letters
        ]

    if any(not letter for letter in window_letters):
        raise ValueError("Window letters cannot contain empty values.")

    if aisle_letters is None:
        aisle_letters = []
    else:
        aisle_letters = [
            str(letter).strip().upper()
            for letter in aisle_letters
        ]

    if any(not letter for letter in aisle_letters):
        raise ValueError("Aisle letters cannot contain empty values.")

    exit_rows = [int(row) for row in exit_rows]

    invalid_window_letters = set(window_letters) - set(letters)
    if invalid_window_letters:
        raise ValueError(
            f"Window letters must be included in seat letters: {invalid_window_letters}."
        )

    invalid_aisle_letters = set(aisle_letters) - set(letters)
    if invalid_aisle_letters:
        raise ValueError(
            f"Aisle letters must be included in seat letters: {invalid_aisle_letters}."
        )

    invalid_exit_rows = [
        row for row in exit_rows
        if row < 1 or row > rows
    ]

    if invalid_exit_rows:
        raise ValueError(
            f"Exit rows must be within available row range: {invalid_exit_rows}."
        )

    allowed_class_types = {
        SeatClass.Type.ECONOMY,
        SeatClass.Type.PREMIUM_ECONOMY,
        SeatClass.Type.BUSINESS,
        SeatClass.Type.FIRST,
    }

    seat_classes = {
        seat_class.class_type: seat_class
        for seat_class in SeatClass.objects.filter(
            airline=airplane.airline
        )
    }

    if SeatClass.Type.ECONOMY not in seat_classes:
        raise ValueError("Economy seat class must be created first.")

    row_to_class_type = {}

    for class_type, row_list in class_rows.items():
        if class_type not in allowed_class_types:
            raise ValueError(f"Invalid seat class type: {class_type}.")

        if class_type not in seat_classes:
            raise ValueError(f"{class_type} seat class must be created first.")

        if row_list is None:
            raise ValueError(f"Rows for class {class_type} cannot be empty.")

        for row in row_list:
            row = int(row)

            if row < 1 or row > rows:
                raise ValueError(f"Row {row} is outside available row range.")

            if row in row_to_class_type:
                raise ValueError(
                    f"Row {row} is assigned to more than one class."
                )

            row_to_class_type[row] = class_type

    with transaction.atomic():
        if airplane.seats.exists():
            raise ValueError("Seats for this airplane already exist.")

        seats = []

        for row in range(1, rows + 1):
            class_type = row_to_class_type.get(
                row,
                SeatClass.Type.ECONOMY
            )
            seat_class = seat_classes[class_type]

            for letter in letters:
                seats.append(
                    AirplaneSeat(
                        airplane=airplane,
                        seat_class=seat_class,
                        row_number=row,
                        seat_letter=letter,
                        is_window=letter in window_letters,
                        is_aisle=letter in aisle_letters,
                        is_exit_row=row in exit_rows,
                        has_extra_legroom=row in exit_rows or row == 1,
                        is_active=True,
                    )
                )

        AirplaneSeat.objects.bulk_create(seats, batch_size=500)

    logger.info(
        "Generated %s seats for airplane %s.",
        len(seats),
        airplane.tail_number,
    )

    return len(seats)