from django.conf import settings
from django.core.mail import send_mail


def send_email(subject, message, recipient_email):
    if not recipient_email:
        return

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient_email],
        fail_silently=False,
    )


def get_user_name(user):
    return user.first_name or user.email


def send_booking_paid_email(booking):
    subject = f"Booking #{booking.id} payment successful"

    message = (
        f"Hello, {get_user_name(booking.user)}!\n\n"
        f"Your booking #{booking.id} has been successfully paid.\n"
        f"Total price: {booking.total_price}.\n\n"
        f"Thank you for using Airport Management System."
    )

    send_email(subject, message, booking.user.email)


def send_booking_expired_email(booking):
    subject = f"Booking #{booking.id} expired"

    message = (
        f"Hello, {get_user_name(booking.user)}!\n\n"
        f"Your booking #{booking.id} has expired because payment was not completed in time.\n"
        f"The reserved tickets were cancelled and the seats are now available again.\n\n"
        f"Airport Management System."
    )

    send_email(subject, message, booking.user.email)


def send_lounge_paid_email(lounge_access):
    subject = f"Lounge access #{lounge_access.id} payment successful"

    message = (
        f"Hello, {get_user_name(lounge_access.user)}!\n\n"
        f"Your lounge access #{lounge_access.id} has been successfully paid.\n"
        f"Lounge: {lounge_access.lounge.name}\n"
        f"Valid until: {lounge_access.valid_until}\n\n"
        f"Airport Management System."
    )

    send_email(subject, message, lounge_access.user.email)


def send_lounge_expired_email(lounge_access):
    subject = f"Lounge access #{lounge_access.id} expired"

    message = (
        f"Hello, {get_user_name(lounge_access.user)}!\n\n"
        f"Your paid lounge access #{lounge_access.id} has expired because payment was not completed in time.\n"
        f"Lounge: {lounge_access.lounge.name}\n\n"
        f"Airport Management System."
    )

    send_email(subject, message, lounge_access.user.email)


def send_lounge_approved_email(lounge_access):
    subject = f"Lounge access #{lounge_access.id} approved"

    message = (
        f"Hello, {get_user_name(lounge_access.user)}!\n\n"
        f"Your lounge access request #{lounge_access.id} has been approved.\n"
        f"Lounge: {lounge_access.lounge.name}\n"
        f"Valid from: {lounge_access.valid_from}\n"
        f"Valid until: {lounge_access.valid_until}\n\n"
        f"Airport Management System."
    )

    send_email(subject, message, lounge_access.user.email)


def send_lounge_rejected_email(lounge_access):
    subject = f"Lounge access #{lounge_access.id} rejected"

    message = (
        f"Hello, {get_user_name(lounge_access.user)}!\n\n"
        f"Your lounge access request #{lounge_access.id} has been rejected.\n"
        f"Lounge: {lounge_access.lounge.name}\n\n"
        f"Airport Management System."
    )

    send_email(subject, message, lounge_access.user.email)