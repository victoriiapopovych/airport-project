from django.utils import timezone

from .models import LoungeAccess

import logging
logger = logging.getLogger(__name__)


def apply_payment_logic(lounge_access, old_is_paid=False):
    logger.info(
        "Applying payment logic for lounge access. Access type: %s, old_is_paid: %s, current_is_paid: %s.",
        lounge_access.access_type,
        old_is_paid,
        lounge_access.is_paid,
    )

    if lounge_access.access_type == LoungeAccess.AccessType.PAID_ACCESS:
        lounge_access.price = lounge_access.lounge.access_price

        if lounge_access.is_paid and not old_is_paid:
            lounge_access.paid_at = timezone.now()
            lounge_access.status = LoungeAccess.Status.APPROVED

            logger.info(
                "Paid lounge access approved. Lounge: %s, user: %s, price: %s.",
                lounge_access.lounge_id,
                lounge_access.user_id,
                lounge_access.price,
            )

        elif not lounge_access.is_paid:
            lounge_access.paid_at = None

            logger.info(
                "Paid lounge access is waiting for payment. Lounge: %s, user: %s, price: %s.",
                lounge_access.lounge_id,
                lounge_access.user_id,
                lounge_access.price,
            )

    else:
        lounge_access.price = 0
        lounge_access.is_paid = True
        lounge_access.paid_at = None
        lounge_access.status = LoungeAccess.Status.APPROVED

        logger.info(
            "Free lounge access approved automatically. Access type: %s, lounge: %s, user: %s.",
            lounge_access.access_type,
            lounge_access.lounge_id,
            lounge_access.user_id,
        )


def get_ticket_flight_number(lounge_access):
    if lounge_access.ticket:
        return lounge_access.ticket.flight.flight_number

    return None