from rest_framework import serializers
from .models import Lounge, LoungeAccess


class LoungeSerializer(serializers.ModelSerializer):
    airport_name = serializers.CharField(source="airport.name", read_only=True)

    class Meta:
        model = Lounge
        fields = ["id", "name", "airport", "airport_name", "location_description", "opening_time", "closing_time", "capacity", "is_active"]


class LoungeAccessSerializer(serializers.ModelSerializer):
    user_name = serializers.StringRelatedField(source="user", read_only=True)
    lounge_name = serializers.CharField(source="lounge.name", read_only=True)
    ticket_flight_number = serializers.SerializerMethodField()

    class Meta:
        model = LoungeAccess
        fields = ["id", "user", "user_name", "lounge", "lounge_name", "ticket", "ticket_flight_number", "access_type", "valid_from", "valid_until", "is_used"]

    def get_ticket_flight_number(self, obj):
        if obj.ticket:
            return obj.ticket.flight.flight_number
        return None

