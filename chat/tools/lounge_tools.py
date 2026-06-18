from lounge.models import Lounge, LoungeAccess


def get_available_lounges(airport_name=None, limit=10):
    lounges = (
        Lounge.objects
        .select_related("airport")
        .filter(is_active=True)
    )

    if airport_name:
        lounges = lounges.filter(airport__name__icontains=airport_name)

    lounges = lounges.order_by("airport__name", "name")[:limit]

    result = []

    for lounge in lounges:
        result.append({
            "lounge_id": lounge.id,
            "name": lounge.name,
            "airport": lounge.airport.name,
            "location": lounge.location_description,
            "opening_time": lounge.opening_time.strftime("%H:%M"),
            "closing_time": lounge.closing_time.strftime("%H:%M"),
            "capacity": lounge.capacity,
            "access_price": str(lounge.access_price),
            "is_active": lounge.is_active,
        })

    return result


def get_lounge_details(lounge_id: int):
    if not lounge_id:
        return {"error": "lounge_id is required."}

    lounge = (
        Lounge.objects
        .select_related("airport")
        .filter(id=lounge_id)
        .first()
    )

    if not lounge:
        return {"error": f"Lounge {lounge_id} was not found."}

    return {
        "lounge_id": lounge.id,
        "name": lounge.name,
        "airport": lounge.airport.name,
        "location": lounge.location_description,
        "opening_time": lounge.opening_time.strftime("%H:%M"),
        "closing_time": lounge.closing_time.strftime("%H:%M"),
        "capacity": lounge.capacity,
        "access_price": str(lounge.access_price),
        "is_active": lounge.is_active,
    }


def get_user_lounge_accesses(user_id: int, status=None, limit=10):
    accesses = (
        LoungeAccess.objects
        .filter(user_id=user_id)
        .select_related(
            "lounge",
            "lounge__airport",
            "ticket",
            "ticket__flight",
        )
    )

    if status:
        accesses = accesses.filter(status__iexact=status)

    accesses = accesses.order_by("-valid_from")[:limit]

    result = []

    for access in accesses:
        result.append({
            "lounge_access_id": access.id,
            "lounge": access.lounge.name,
            "airport": access.lounge.airport.name,
            "ticket_id": access.ticket_id if access.ticket_id else "",
            "flight_number": access.ticket.flight.flight_number if access.ticket else "",
            "access_type": access.access_type,
            "price": str(access.price),
            "is_paid": access.is_paid,
            "valid_from": access.valid_from.isoformat(),
            "valid_until": access.valid_until.isoformat(),
            "is_used": access.is_used,
            "status": access.status,
        })

    return result


def get_lounge_access_details(user_id: int, lounge_access_id: int):
    if not lounge_access_id:
        return {"error": "lounge_access_id is required."}

    access = (
        LoungeAccess.objects
        .filter(id=lounge_access_id, user_id=user_id)
        .select_related(
            "lounge",
            "lounge__airport",
            "ticket",
            "ticket__flight",
            "ticket__airplane_seat",
            "ticket__airplane_seat__seat_class",
        )
        .first()
    )

    if not access:
        return {
            "error": f"Lounge access {lounge_access_id} was not found for this user."
        }

    ticket_data = {}

    if access.ticket:
        ticket_data = {
            "ticket_id": access.ticket.id,
            "flight_number": access.ticket.flight.flight_number,
            "seat_number": access.ticket.airplane_seat.seat_number,
            "seat_class": access.ticket.airplane_seat.seat_class.class_type,
            "ticket_status": access.ticket.status,
        }

    return {
        "lounge_access_id": access.id,
        "lounge": {
            "lounge_id": access.lounge.id,
            "name": access.lounge.name,
            "airport": access.lounge.airport.name,
            "location": access.lounge.location_description,
        },
        "ticket": ticket_data,
        "access_type": access.access_type,
        "price": str(access.price),
        "is_paid": access.is_paid,
        "valid_from": access.valid_from.isoformat(),
        "valid_until": access.valid_until.isoformat(),
        "is_used": access.is_used,
        "status": access.status,
    }
