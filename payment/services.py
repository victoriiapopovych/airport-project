import stripe

from django.conf import settings
from rest_framework import serializers

from lounge.models import LoungeAccess
from lounge.services import apply_payment_logic

from ticket.models import Booking, Ticket

from .models import Payment

from datetime import timedelta
from django.utils import timezone

from notifications.services import send_booking_paid_email, send_booking_expired_email, send_lounge_paid_email, send_lounge_expired_email

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(user, payment_type, booking_id=None, lounge_access_id=None):
    if payment_type == Payment.TypeChoices.BOOKING:
        try:
            booking = Booking.objects.get(id=booking_id, user=user)
        except Booking.DoesNotExist:
            raise serializers.ValidationError("Booking not found.")

        return create_booking_checkout_session(booking)

    if payment_type == Payment.TypeChoices.LOUNGE:
        try:
            lounge_access = LoungeAccess.objects.get(id=lounge_access_id, user=user)
        except LoungeAccess.DoesNotExist:
            raise serializers.ValidationError("Lounge access not found.")

        return create_lounge_checkout_session(lounge_access)

    raise serializers.ValidationError("Invalid payment type.")


def create_booking_checkout_session(booking):
    if booking.status != Booking.Status.PENDING:
        raise serializers.ValidationError("Only pending booking can be paid.")

    if booking.total_price <= 0:
        raise serializers.ValidationError("Booking total price must be greater than 0.")

    existing_payment = Payment.objects.filter(
        booking=booking,
        status=Payment.StatusChoices.PENDING,
        stripe_session_id__isnull=False,
    ).first()

    if existing_payment:
        return existing_payment.checkout_url
    payment = Payment.objects.create(
        user=booking.user,
        booking=booking,
        payment_type=Payment.TypeChoices.BOOKING,
        amount=booking.total_price,
        currency=settings.STRIPE_CURRENCY.upper(),
        status=Payment.StatusChoices.PENDING,
    )

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=[
            {
                "price_data": {
                    "currency": settings.STRIPE_CURRENCY.lower(),
                    "product_data": {
                        "name": f"Booking #{booking.id}",
                    },
                    "unit_amount": int(booking.total_price * 100),
                },
                "quantity": 1,
            }
        ],
        metadata={
            "payment_id": payment.id,
            "payment_type": Payment.TypeChoices.BOOKING,
            "booking_id": booking.id,
        },

        expires_at=int(
            (timezone.now() + timedelta(minutes=30)).timestamp()
        ),

        success_url=settings.STRIPE_SUCCESS_URL,
        cancel_url=settings.STRIPE_CANCEL_URL,
    )

    payment.stripe_session_id = session.id
    payment.checkout_url = session.url
    payment.save(update_fields=["stripe_session_id", "checkout_url"])

    return session.url


def handle_successful_checkout(session):
    stripe_session_id = session["id"]

    try:
        payment = Payment.objects.get(stripe_session_id=stripe_session_id)
    except Payment.DoesNotExist:
        raise serializers.ValidationError("Payment not found.")

    if payment.status == Payment.StatusChoices.PAID:
        return payment
    
    if payment.status != Payment.StatusChoices.PENDING:
        return payment

    payment.status = Payment.StatusChoices.PAID
    payment.save(update_fields=["status"])

    if payment.payment_type == Payment.TypeChoices.BOOKING and payment.booking:
        booking = payment.booking

        if booking.status != Booking.Status.PENDING:
            raise serializers.ValidationError("Booking is not available for payment.")

        booking.status = Booking.Status.PAID
        booking.save(update_fields=["status"])

        Ticket.objects.filter(booking=booking).update(
            status=Ticket.Status.PAID
        )

        send_booking_paid_email(booking)

    if payment.payment_type == Payment.TypeChoices.LOUNGE and payment.lounge_access:
        lounge_access = payment.lounge_access
        old_is_paid = lounge_access.is_paid

        lounge_access.is_paid = True
        apply_payment_logic(lounge_access, old_is_paid)
        lounge_access.save(
            update_fields=[
                "is_paid",
                "paid_at",
                "status",
                "price",
            ]
        )

        send_lounge_paid_email(lounge_access)

    return payment


def create_lounge_checkout_session(lounge_access):
    if lounge_access.access_type != LoungeAccess.AccessType.PAID_ACCESS:
        raise serializers.ValidationError("Only paid lounge access can be paid.")

    if lounge_access.status != LoungeAccess.Status.PENDING:
        raise serializers.ValidationError("Only pending lounge access can be paid.")

    if lounge_access.is_paid:
        raise serializers.ValidationError("This lounge access is already paid.")

    if lounge_access.price <= 0:
        raise serializers.ValidationError("Lounge access price must be greater than 0.")

    existing_payment = Payment.objects.filter(
        lounge_access=lounge_access,
        status=Payment.StatusChoices.PENDING,
        stripe_session_id__isnull=False,
    ).first()

    if existing_payment:
        return existing_payment.checkout_url

    payment = Payment.objects.create(
        user=lounge_access.user,
        lounge_access=lounge_access,
        payment_type=Payment.TypeChoices.LOUNGE,
        amount=lounge_access.price,
        currency=settings.STRIPE_CURRENCY.upper(),
        status=Payment.StatusChoices.PENDING,
    )

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=[
            {
                "price_data": {
                    "currency": settings.STRIPE_CURRENCY.lower(),
                    "product_data": {
                        "name": f"Lounge access #{lounge_access.id}",
                    },
                    "unit_amount": int(lounge_access.price * 100),
                },
                "quantity": 1,
            }
        ],
        metadata={
            "payment_id": payment.id,
            "payment_type": Payment.TypeChoices.LOUNGE,
            "lounge_access_id": lounge_access.id,
        },

        expires_at=int(
            (timezone.now() + timedelta(minutes=30)).timestamp()
        ),

        success_url=settings.STRIPE_SUCCESS_URL,
        cancel_url=settings.STRIPE_CANCEL_URL,
    )

    payment.stripe_session_id = session.id
    payment.checkout_url = session.url
    payment.save(update_fields=["stripe_session_id", "checkout_url"])

    return session.url


def handle_expired_checkout(session):
    stripe_session_id = session["id"]

    try:
        payment = Payment.objects.get(stripe_session_id=stripe_session_id)
    except Payment.DoesNotExist:
        raise serializers.ValidationError("Payment not found.")

    if payment.status != Payment.StatusChoices.PENDING:
        return payment

    payment.status = Payment.StatusChoices.EXPIRED
    payment.save(update_fields=["status"])

    if payment.payment_type == Payment.TypeChoices.BOOKING and payment.booking:
        booking = payment.booking
        booking.status = Booking.Status.EXPIRED
        booking.save(update_fields=["status"])

        Ticket.objects.filter(booking=booking).update(
            status=Ticket.Status.CANCELLED
        )

        send_booking_expired_email(booking)

    if payment.payment_type == Payment.TypeChoices.LOUNGE and payment.lounge_access:
        lounge_access = payment.lounge_access
        lounge_access.status = LoungeAccess.Status.CANCELLED
        lounge_access.save(update_fields=["status"])

        send_lounge_expired_email(lounge_access)

    return payment


def cancel_pending_payment_for_booking(booking):
    payment = Payment.objects.filter(
        booking=booking,
        status=Payment.StatusChoices.PENDING,
        stripe_session_id__isnull=False,
    ).first()

    if not payment:
        return None

    try:
        stripe.checkout.Session.expire(payment.stripe_session_id)
    except stripe.error.InvalidRequestError:
        pass

    payment.status = Payment.StatusChoices.CANCELLED
    payment.save(update_fields=["status"])

    return payment

