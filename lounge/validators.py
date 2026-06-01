from rest_framework import serializers
from django.utils import timezone

from .models import LoungeAccess


def validate_access_dates(valid_from, valid_until):
    if valid_from and valid_until and valid_until <= valid_from:
        raise serializers.ValidationError("valid_until must be later than valid_from.")

    if valid_until and valid_until <= timezone.now():
        raise serializers.ValidationError("valid_until must be in the future.")


def validate_lounge_working_hours(lounge, valid_from, valid_until):
    if not lounge or not valid_from or not valid_until:
        return

    if (
        valid_from.time() < lounge.opening_time
        or valid_until.time() > lounge.closing_time
    ):
        raise serializers.ValidationError("Selected access time must be within lounge working hours.")


def validate_paid_access_price(access_type, lounge):
    if (
        access_type == LoungeAccess.AccessType.PAID_ACCESS
        and lounge
        and lounge.access_price <= 0
    ):
        raise serializers.ValidationError("This lounge does not have a valid paid access price.")


def validate_lounge_capacity(lounge, valid_from, valid_until):
    active_accesses = LoungeAccess.objects.filter(
        lounge=lounge,
        status=LoungeAccess.Status.APPROVED,
        is_used=True,
        valid_from__lt=valid_until,
        valid_until__gt=valid_from,
    ).count()

    if active_accesses >= lounge.capacity:
        raise serializers.ValidationError("Lounge capacity exceeded for selected time.")