from rest_framework import serializers

from lounge.models import LoungeAccess
from ticket.models import Booking

from .models import Payment


class CreateCheckoutSessionSerializer(serializers.Serializer):
    payment_type = serializers.ChoiceField(choices=Payment.TypeChoices.choices)
    booking_id = serializers.IntegerField(required=False, allow_null=True)
    lounge_access_id = serializers.IntegerField(required=False, allow_null=True)

    def validate(self, attrs):
        request = self.context["request"]

        payment_type = attrs.get("payment_type")
        booking_id = attrs.get("booking_id")
        lounge_access_id = attrs.get("lounge_access_id")

        if payment_type == Payment.TypeChoices.BOOKING:
            if not booking_id:
                raise serializers.ValidationError(
                    {"booking_id": "This field is required."}
                )

            if lounge_access_id:
                raise serializers.ValidationError(
                    {"lounge_access_id": "This field is not allowed for BOOKING payment."}
                )

            if not Booking.objects.filter(id=booking_id, user=request.user).exists():
                raise serializers.ValidationError({"booking_id": "Booking not found."})

        if payment_type == Payment.TypeChoices.LOUNGE:
            if not lounge_access_id:
                raise serializers.ValidationError({"lounge_access_id": "This field is required."})

            if booking_id:
                raise serializers.ValidationError({"booking_id": "This field is not allowed for LOUNGE payment."})

            if not LoungeAccess.objects.filter(id=lounge_access_id, user=request.user).exists():
                raise serializers.ValidationError({"lounge_access_id": "Lounge access not found."})

        return attrs