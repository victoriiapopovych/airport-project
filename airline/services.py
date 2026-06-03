from .models import AirplaneSeat, SeatClass

import logging
logger = logging.getLogger(__name__)


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
        "Starting airplane seats generation for airplane %s.",
        airplane.tail_number,
    )

    if letters is None:
        letters = ["A", "B", "C", "D", "E", "F"]

    if class_rows is None:
        class_rows = {}

    if exit_rows is None:
        exit_rows = []

    rows = int(rows)

    if rows <= 0:
        logger.warning(
            "Airplane seats generation failed for airplane %s: rows count must be greater than 0.",
            airplane.tail_number,
        )
        raise ValueError("Rows count must be greater than 0.")

    if not letters:
        logger.warning(
            "Airplane seats generation failed for airplane %s: letters list is empty.",
            airplane.tail_number,
        )
        raise ValueError("Letters list cannot be empty.")

    letters = [str(letter).upper() for letter in letters]

    if len(letters) != len(set(letters)):
        logger.warning(
            "Airplane seats generation failed for airplane %s: duplicate seat letters were provided.",
            airplane.tail_number,
        )
        raise ValueError("Seat letters must be unique.")

    if window_letters is None:
        window_letters = [letters[0], letters[-1]]

    if aisle_letters is None:
        aisle_letters = []

    window_letters = [str(letter).upper() for letter in window_letters]
    aisle_letters = [str(letter).upper() for letter in aisle_letters]
    exit_rows = [int(row) for row in exit_rows]

    if set(window_letters) - set(letters):
        logger.warning(
            "Airplane seats generation failed for airplane %s: invalid window letters %s.",
            airplane.tail_number,
            window_letters,
        )
        raise ValueError("Window letters must be included in seat letters.")

    if set(aisle_letters) - set(letters):
        logger.warning(
            "Airplane seats generation failed for airplane %s: invalid aisle letters %s.",
            airplane.tail_number,
            aisle_letters,
        )
        raise ValueError("Aisle letters must be included in seat letters.")

    if any(row < 1 or row > rows for row in exit_rows):
        logger.warning(
            "Airplane seats generation failed for airplane %s: exit rows %s are outside available rows.",
            airplane.tail_number,
            exit_rows,
        )
        raise ValueError("Exit rows must be within the available row range.")

    if airplane.seats.exists():
        logger.warning(
            "Airplane seats generation skipped for airplane %s: seats already exist.",
            airplane.tail_number,
        )
        raise ValueError("Seats for this airplane already exist.")

    seat_classes = {
        seat_class.class_type: seat_class
        for seat_class in SeatClass.objects.filter(airline=airplane.airline)
    }

    if SeatClass.Type.ECONOMY not in seat_classes:
        logger.warning(
            "Airplane seats generation failed for airplane %s: economy seat class does not exist for airline %s.",
            airplane.tail_number,
            airplane.airline.name,
        )
        raise ValueError("Economy seat class must be created first.")

    allowed_class_types = [
        SeatClass.Type.ECONOMY,
        SeatClass.Type.PREMIUM_ECONOMY,
        SeatClass.Type.BUSINESS,
        SeatClass.Type.FIRST,
    ]

    row_to_class_type = {}

    for class_type, row_list in class_rows.items():
        if class_type not in allowed_class_types:
            logger.warning(
                "Airplane seats generation failed for airplane %s: invalid seat class type %s.",
                airplane.tail_number,
                class_type,
            )
            raise ValueError(f"Invalid seat class type: {class_type}.")

        if class_type not in seat_classes:
            logger.warning(
                "Airplane seats generation failed for airplane %s: %s seat class does not exist for airline %s.",
                airplane.tail_number,
                class_type,
                airplane.airline.name,
            )
            raise ValueError(f"{class_type} seat class must be created first.")

        for row in row_list:
            row = int(row)

            if row < 1 or row > rows:
                logger.warning(
                    "Airplane seats generation failed for airplane %s: row %s is outside available range.",
                    airplane.tail_number,
                    row,
                )
                raise ValueError(f"Row {row} is outside the available row range.")

            if row in row_to_class_type:
                logger.warning(
                    "Airplane seats generation failed for airplane %s: row %s is assigned to more than one class.",
                    airplane.tail_number,
                    row,
                )
                raise ValueError(f"Row {row} is assigned to more than one class.")

            row_to_class_type[row] = class_type

    seats = []

    for row in range(1, rows + 1):
        class_type = row_to_class_type.get(row, SeatClass.Type.ECONOMY)
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

    AirplaneSeat.objects.bulk_create(seats)

    logger.info(
        "Generated %s airplane seats for airplane %s.",
        len(seats),
        airplane.tail_number,
    )

    return len(seats)