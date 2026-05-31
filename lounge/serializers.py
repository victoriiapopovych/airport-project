from rest_framework import serializers
from .models import Lounge, LoungeAccess

from django.utils import timezone


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


class LoungeDetailSerializer(serializers.ModelSerializer):
    airport_name = serializers.CharField(source="airport.name", read_only=True)

    class Meta:
        model = Lounge
        fields = ["id", "name", "airport", "airport_name", "location_description", "opening_time", "closing_time", "capacity", "access_price", "is_active"]


class LoungeListSerializer(serializers.ModelSerializer):
    airport_name = serializers.CharField(source="airport.name", read_only=True)

    class Meta:
        model = Lounge
        fields = ["id", "name", "airport_name", "opening_time", "closing_time", "access_price", "is_active"]


class LoungeAccessDetailSerializer(serializers.ModelSerializer):
    user_name = serializers.StringRelatedField(source="user", read_only=True)
    lounge_name = serializers.CharField(source="lounge.name", read_only=True)
    ticket_flight_number = serializers.SerializerMethodField()

    class Meta:
        model = LoungeAccess
        fields = ["id", "user", "user_name", "lounge", "lounge_name", "ticket", "ticket_flight_number", "access_type","price", "is_paid", "paid_at", "valid_from", "valid_until", "is_used", "status"]
        read_only_fields = ["user", "status", "is_used", "price", "is_paid", "paid_at", "ticket_flight_number"]

    def get_ticket_flight_number(self, obj):
        if obj.ticket:
            return obj.ticket.flight_seat.flight.flight_number
        return None
    
    
class LoungeAccessListSerializer(serializers.ModelSerializer):
    user_name = serializers.StringRelatedField(source="user", read_only=True)
    lounge_name = serializers.CharField(source="lounge.name", read_only=True)
    ticket_flight_number = serializers.SerializerMethodField()

    class Meta:
        model = LoungeAccess
        fields = ["id", "user_name", "lounge_name", "ticket_flight_number", "access_type", "price", "is_paid", "valid_until", "is_used", "status"]

    def get_ticket_flight_number(self, obj):
        if obj.ticket:
            return obj.ticket.flight_seat.flight.flight_number
        return None
    

class LoungeAccessOperatorUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoungeAccess
        fields = ["status", "access_type", "is_paid", "paid_at", "valid_from", "valid_until", "is_used"]

    def validate(self, attrs):
        valid_from = attrs.get("valid_from", self.instance.valid_from)
        valid_until = attrs.get("valid_until", self.instance.valid_until)
        is_paid = attrs.get("is_paid", self.instance.is_paid)
        is_used = attrs.get("is_used", self.instance.is_used)
        access_type = attrs.get("access_type", self.instance.access_type)

        validate_access_dates(valid_from, valid_until)
        validate_lounge_working_hours(self.instance.lounge, valid_from, valid_until)
        

        if (
            access_type == LoungeAccess.AccessType.PAID_ACCESS
            and is_used
            and not is_paid
        ):
            raise serializers.ValidationError("Access cannot be used before payment.")

        if is_used and not self.instance.is_used:
            validate_lounge_capacity(
                self.instance.lounge,
                valid_from,
                valid_until,
            )

        return attrs

    def update(self, instance, validated_data):
        old_is_paid = instance.is_paid
        instance = super().update(instance, validated_data)
        apply_payment_logic(instance, old_is_paid)
        instance.save()
        return instance


class LoungeAccessAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoungeAccess
        fields = ["id", "user", "lounge", "ticket", "access_type", "price", "is_paid", "paid_at", "valid_from", "valid_until", "is_used", "status"]
        read_only_fields = ["id"]

    def validate(self, attrs):
        valid_from = attrs.get("valid_from", self.instance.valid_from if self.instance else None)
        valid_until = attrs.get("valid_until", self.instance.valid_until if self.instance else None)
        access_type = attrs.get("access_type", self.instance.access_type if self.instance else None)
        lounge = attrs.get("lounge", self.instance.lounge if self.instance else None)

        validate_access_dates(valid_from, valid_until)
        validate_lounge_working_hours(lounge, valid_from, valid_until)
        validate_paid_access_price(access_type, lounge)

        if lounge and not lounge.is_active:
            raise serializers.ValidationError("This lounge is currently inactive.")

        return attrs

    def create(self, validated_data):
        lounge_access = LoungeAccess(**validated_data)
        apply_payment_logic(lounge_access)
        lounge_access.save()
        return lounge_access

    def update(self, instance, validated_data):
        old_is_paid = instance.is_paid
        instance = super().update(instance, validated_data)
        apply_payment_logic(instance, old_is_paid)
        instance.save()
        return instance


class LoungeAccessCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoungeAccess
        fields = ["id", "lounge", "ticket", "access_type", "valid_from", "valid_until"]
        read_only_fields = ["id"]

    def validate(self, attrs):
        request = self.context["request"]

        ticket = attrs.get("ticket")
        access_type = attrs["access_type"]

        validate_access_dates(attrs["valid_from"], attrs["valid_until"])
        validate_lounge_working_hours(attrs["lounge"], attrs["valid_from"], attrs["valid_until"])
        validate_paid_access_price(access_type, attrs["lounge"])

        if not attrs["lounge"].is_active:
            raise serializers.ValidationError("This lounge is currently inactive.")

        if ticket and ticket.booking.user != request.user:
            raise serializers.ValidationError("You can use only your own ticket.")

        if ticket and ticket.status != ticket.Status.PAID:
            raise serializers.ValidationError("Lounge access is available only for paid tickets.")
        
        if ticket and LoungeAccess.objects.filter(ticket=ticket).exists():
            raise serializers.ValidationError("Lounge access for this ticket already exists.")
        
        if ticket:
            departure_airport = ticket.flight_seat.flight.route.departure_airport

            if attrs["lounge"].airport != departure_airport:
                raise serializers.ValidationError("Lounge must be located in the departure airport of the ticket flight.")

        if access_type == LoungeAccess.AccessType.BUSINESS_CLASS:
            if not ticket:
                raise serializers.ValidationError("Business class access requires a ticket.")

            seat_class = ticket.flight_seat.airplane_seat.seat_class

            if not seat_class.lounge_access:
                raise serializers.ValidationError("This ticket class does not include lounge access.")

        return attrs

    def create(self, validated_data):
        lounge_access = LoungeAccess(**validated_data)
        apply_payment_logic(lounge_access)
        lounge_access.save()
        return lounge_access

    
