from django.utils import timezone

from .models import LoungeAccess


def apply_payment_logic(lounge_access, old_is_paid=False):
    if lounge_access.access_type == LoungeAccess.AccessType.PAID_ACCESS:
        lounge_access.price = lounge_access.lounge.access_price

        if lounge_access.is_paid and not old_is_paid:
            lounge_access.paid_at = timezone.now()
            lounge_access.status = LoungeAccess.Status.APPROVED

        elif not lounge_access.is_paid:
            lounge_access.paid_at = None

    else:
        lounge_access.price = 0
        lounge_access.is_paid = True
        lounge_access.paid_at = None
        lounge_access.status = LoungeAccess.Status.APPROVED


def get_ticket_flight_number(lounge_access):
    if lounge_access.ticket:
        return lounge_access.ticket.flight_seat.flight.flight_number

    return None