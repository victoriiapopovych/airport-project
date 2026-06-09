from rest_framework import serializers
from .models import Lounge, LoungeAccess

from .services import apply_payment_logic, get_ticket_flight_number

from .validators import validate_access_dates, validate_lounge_working_hours, validate_paid_access_price, validate_lounge_capacity

from payment.services import create_lounge_checkout_session


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
        return get_ticket_flight_number(obj)
    
    
class LoungeAccessListSerializer(serializers.ModelSerializer):
    user_name = serializers.StringRelatedField(source="user", read_only=True)
    lounge_name = serializers.CharField(source="lounge.name", read_only=True)
    ticket_flight_number = serializers.SerializerMethodField()

    class Meta:
        model = LoungeAccess
        fields = ["id", "user_name", "lounge_name", "ticket_flight_number", "access_type", "price", "is_paid", "valid_until", "is_used", "status"]

    def get_ticket_flight_number(self, obj):
        return get_ticket_flight_number(obj)

class LoungeAccessOperatorUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoungeAccess
        fields = ["status", "valid_from", "valid_until", "is_used"]

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
        return super().update(instance, validated_data)


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
        
        if access_type != LoungeAccess.AccessType.PAID_ACCESS and not ticket:
            raise serializers.ValidationError("This access type requires a ticket.")
        
        if access_type == LoungeAccess.AccessType.PAID_ACCESS and ticket:
            raise serializers.ValidationError("Paid access should be created without ticket.")

        if ticket and ticket.booking.user != request.user:
            raise serializers.ValidationError("You can use only your own ticket.")

        if ticket and ticket.status != ticket.Status.PAID:
            raise serializers.ValidationError("Lounge access is available only for paid tickets.")
        
        if ticket and LoungeAccess.objects.filter(ticket=ticket).exists():
            raise serializers.ValidationError("Lounge access for this ticket already exists.")
        
        if ticket:
            departure_airport = ticket.flight.route.departure_airport

            if attrs["lounge"].airport != departure_airport:
                raise serializers.ValidationError("Lounge must be located in the departure airport of the ticket flight.")

        if access_type == LoungeAccess.AccessType.BUSINESS_CLASS:
            if not ticket:
                raise serializers.ValidationError("Business class access requires a ticket.")

            seat_class = ticket.airplane_seat.seat_class

            if not seat_class.lounge_access:
                raise serializers.ValidationError("This ticket class does not include lounge access.")

        return attrs

    def create(self, validated_data):
        lounge_access = LoungeAccess(**validated_data)
        apply_payment_logic(lounge_access)
        lounge_access.save()

        if lounge_access.access_type == LoungeAccess.AccessType.PAID_ACCESS:
            create_lounge_checkout_session(lounge_access)

        return lounge_access

    
