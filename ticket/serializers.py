from rest_framework import serializers
from .models import TicketClass, Booking, Ticket


class TicketClassSerializer(serializers.ModelSerializer):

    class Meta:
        model = TicketClass
        fields = ["id", "class_type", "baggage_kg", "priority_boarding", "lounge_access", "extra_price"]


class BookingDetailSerializer(serializers.ModelSerializer):
    user_name = serializers.StringRelatedField(source="user", read_only=True)

    class Meta:
        model = Booking
        fields = ["id", "user", "user_name", "created_at", "status", "total_price"]
        read_only_fields = ["user", "created_at", "status", "total_price"]



class BookingListSerializer(serializers.ModelSerializer):
    user_name = serializers.StringRelatedField(source="user", read_only=True)

    class Meta:
        model = Booking
        fields = ["id", "user_name", "created_at", "status", "total_price"]


class TicketDetailSerializer(serializers.ModelSerializer):
    flight_number = serializers.CharField(source="flight.flight_number", read_only=True)
    ticket_class_name = serializers.StringRelatedField(source="ticket_class", read_only=True)

    class Meta:
        model = Ticket
        fields = ["id", "booking", "flight", "flight_number", "ticket_class", "ticket_class_name", "passenger_first_name", "passenger_last_name", "seat_number", "price", "status"]
        read_only_fields = ["price", "status"]

class TicketListSerializer(serializers.ModelSerializer):
    flight_number = serializers.CharField(source="flight.flight_number", read_only=True)

    class Meta:
        model = Ticket
        fields = ["id", "flight_number", "passenger_first_name", "passenger_last_name", "seat_number", "price", "status"]

class BookingStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ["status"]

class TicketStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["status"]

class BookingManagerAdminUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ["status"]