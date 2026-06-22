from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
from rest_framework import serializers

from user.models import User
from location.models import Country, City, Airport
from airline.models import Airline, AirplaneType, Airplane, SeatClass, AirplaneSeat
from flight.models import Route, Flight
from ticket.models import Booking, Ticket
from ticket.services import calculate_ticket_price, create_booking, cancel_booking
from django.db import IntegrityError


class BookingServiceTests(TestCase):

    def setUp(self):
        self.country = Country.objects.create(
            name="Germany",
            code="DE",
        )

        self.city = City.objects.create(
            name="Berlin",
            country=self.country,
        )

        self.departure_airport = Airport.objects.create(
            name="Berlin Brandenburg Airport",
            code="BER",
            city=self.city,
        )

        self.arrival_airport = Airport.objects.create(
            name="Munich Airport",
            code="MUC",
            city=self.city,
        )

        self.airline = Airline.objects.create(
            name="Lufthansa",
            iata_code="LH",
            country=self.country,
        )

        self.airplane_type = AirplaneType.objects.create(
            manufacturer="Airbus",
            code="A320",
        )

        self.airplane = Airplane.objects.create(
            tail_number="D-ABCD",
            airline=self.airline,
            airplane_type=self.airplane_type,
            manufactured_year=2020,
            num_of_passengers=180,
            crew_count=6,
        )

        self.seat_class = SeatClass.objects.create(
            airline=self.airline,
            class_type=SeatClass.Type.ECONOMY,
            extra_price=Decimal("50.00"),
            baggage_kg=20,
        )

        self.seat = AirplaneSeat.objects.create(
            airplane=self.airplane,
            seat_class=self.seat_class,
            row_number=1,
            seat_letter="A",
        )

        self.second_seat = AirplaneSeat.objects.create(
            airplane=self.airplane,
            seat_class=self.seat_class,
            row_number=1,
            seat_letter="B",
        )

        self.route = Route.objects.create(
            departure_airport=self.departure_airport,
            arrival_airport=self.arrival_airport,
            distance_km=500,
            estimated_duration=timedelta(hours=1),
        )

        self.flight = Flight.objects.create(
            flight_number="LH123",
            route=self.route,
            airline=self.airline,
            airplane=self.airplane,
            departure_time=timezone.now() + timedelta(days=1),
            arrival_time=timezone.now() + timedelta(days=1, hours=2),
            status=Flight.Status.SCHEDULED,
            base_price=Decimal("100.00"),
        )

        self.user = User.objects.create_user(
            email="user@example.com",
            password="testpass123",
            passport_number="AA123456",
            is_verified=True,
        )

    def test_calculate_ticket_price(self):
        price = calculate_ticket_price(
            self.flight,
            self.seat,
        )

        self.assertEqual(
            price,
            Decimal("150.00"),
        )

    def test_create_booking_success(self):
        tickets_data = [
            {
                "flight": self.flight,
                "airplane_seat": self.seat,
                "passenger_first_name": "John",
                "passenger_last_name": "Doe",
            }
        ]

        booking = create_booking(
            user=self.user,
            tickets_data=tickets_data,
        )

        self.assertEqual(booking.user, self.user)
        self.assertEqual(booking.status, Booking.Status.PENDING)
        self.assertEqual(booking.total_price, Decimal("150.00"))

        self.assertEqual(Ticket.objects.count(), 1)

        ticket = Ticket.objects.first()

        self.assertEqual(ticket.booking, booking)
        self.assertEqual(ticket.flight, self.flight)
        self.assertEqual(ticket.airplane_seat, self.seat)
        self.assertEqual(ticket.passenger_first_name, "John")
        self.assertEqual(ticket.passenger_last_name, "Doe")
        self.assertEqual(ticket.price, Decimal("150.00"))
        self.assertEqual(ticket.status, Ticket.Status.PENDING)

    @patch("ticket.services.Ticket.objects.bulk_create")
    def test_create_booking_integrity_error(
        self,
        mock_bulk_create,
    ):
        mock_bulk_create.side_effect = IntegrityError()

        tickets_data = [
            {
                "flight": self.flight,
                "airplane_seat": self.seat,
                "passenger_first_name": "John",
                "passenger_last_name": "Doe",
            }
        ]

        with self.assertRaises(serializers.ValidationError):
            create_booking(
                user=self.user,
                tickets_data=tickets_data,
            )

    def test_create_booking_with_multiple_tickets(self):
        tickets_data = [
            {
                "flight": self.flight,
                "airplane_seat": self.seat,
                "passenger_first_name": "John",
                "passenger_last_name": "Doe",
            },
            {
                "flight": self.flight,
                "airplane_seat": self.second_seat,
                "passenger_first_name": "Jane",
                "passenger_last_name": "Doe",
            },
        ]

        booking = create_booking(
            user=self.user,
            tickets_data=tickets_data,
        )

        self.assertEqual(Ticket.objects.count(), 2)
        self.assertEqual(booking.total_price, Decimal("300.00"))

        passenger_names = set(
            Ticket.objects.values_list(
                "passenger_first_name",
                flat=True,
            )
        )

        self.assertEqual(
            passenger_names,
            {"John", "Jane"},
        )

    @patch("ticket.services.cancel_pending_payment_for_booking")
    def test_cancel_booking_changes_booking_status(self, mock_cancel_payment):
        booking = Booking.objects.create(
            user=self.user,
            status=Booking.Status.PENDING,
            total_price=Decimal("150.00"),
        )

        Ticket.objects.create(
            booking=booking,
            flight=self.flight,
            airplane_seat=self.seat,
            passenger_first_name="John",
            passenger_last_name="Doe",
            price=Decimal("150.00"),
            status=Ticket.Status.PENDING,
        )

        cancel_booking(booking)

        booking.refresh_from_db()

        self.assertEqual(booking.status, Booking.Status.CANCELLED)
        mock_cancel_payment.assert_called_once_with(booking)

    @patch("ticket.services.cancel_pending_payment_for_booking")
    def test_cancel_booking_cancels_tickets(self, mock_cancel_payment):
        booking = Booking.objects.create(
            user=self.user,
            status=Booking.Status.PENDING,
            total_price=Decimal("300.00"),
        )

        ticket_1 = Ticket.objects.create(
            booking=booking,
            flight=self.flight,
            airplane_seat=self.seat,
            passenger_first_name="John",
            passenger_last_name="Doe",
            price=Decimal("150.00"),
            status=Ticket.Status.PENDING,
        )

        ticket_2 = Ticket.objects.create(
            booking=booking,
            flight=self.flight,
            airplane_seat=self.second_seat,
            passenger_first_name="Jane",
            passenger_last_name="Doe",
            price=Decimal("150.00"),
            status=Ticket.Status.PENDING,
        )

        cancel_booking(booking)

        ticket_1.refresh_from_db()
        ticket_2.refresh_from_db()

        self.assertEqual(
            ticket_1.status,
            Ticket.Status.CANCELLED,
        )

        self.assertEqual(
            ticket_2.status,
            Ticket.Status.CANCELLED,
        )

    @patch("ticket.services.cancel_pending_payment_for_booking")
    def test_cancel_booking_ignores_already_cancelled_tickets(
        self,
        mock_cancel_payment,
    ):
        booking = Booking.objects.create(
            user=self.user,
            status=Booking.Status.PENDING,
            total_price=Decimal("300.00"),
        )

        active_ticket = Ticket.objects.create(
            booking=booking,
            flight=self.flight,
            airplane_seat=self.seat,
            passenger_first_name="John",
            passenger_last_name="Doe",
            price=Decimal("150.00"),
            status=Ticket.Status.PENDING,
        )

        cancelled_ticket = Ticket.objects.create(
            booking=booking,
            flight=self.flight,
            airplane_seat=self.second_seat,
            passenger_first_name="Jane",
            passenger_last_name="Doe",
            price=Decimal("150.00"),
            status=Ticket.Status.CANCELLED,
        )

        cancel_booking(booking)

        active_ticket.refresh_from_db()
        cancelled_ticket.refresh_from_db()

        self.assertEqual(
            active_ticket.status,
            Ticket.Status.CANCELLED,
        )

        self.assertEqual(
            cancelled_ticket.status,
            Ticket.Status.CANCELLED,
        )