from django.test import TestCase
from rest_framework import serializers

from ticket.validators import validate_ticket_limit, validate_duplicate_seats, validate_same_flight, validate_seats_belong_to_flight_airplane, validate_flight_status, validate_flight_departure, validate_passenger_name, validate_available_seats

from datetime import timedelta
from django.utils import timezone

from decimal import Decimal

from user.models import User
from location.models import Country, City, Airport
from airline.models import Airline, AirplaneType, Airplane, SeatClass, AirplaneSeat
from flight.models import Route, Flight
from ticket.models import Booking, Ticket


class TicketValidatorsTests(TestCase):

    def test_validate_ticket_limit_empty_list(self):
        with self.assertRaises(serializers.ValidationError):
            validate_ticket_limit([])

    def test_validate_ticket_limit_success(self):
        tickets = [1]

        validate_ticket_limit(tickets)

    def test_validate_ticket_limit_exceeded(self):
        tickets = [1] * 11

        with self.assertRaises(serializers.ValidationError):
            validate_ticket_limit(tickets)

    def test_validate_passenger_name_success(self):
        result = validate_passenger_name("John", "Passenger first name")

        self.assertEqual(result, "John")

    def test_validate_passenger_name_strip_spaces(self):
        result = validate_passenger_name("  John  ", "Passenger first name")

        self.assertEqual(result, "John")

    def test_validate_passenger_name_empty_error(self):
        with self.assertRaises(serializers.ValidationError):
            validate_passenger_name("   ", "Passenger first name")


class FlightValidatorTests(TestCase):

    def test_validate_flight_status_scheduled_success(self):
        flight = type(
            "Flight",
            (),
            {
                "status": "scheduled",
                "flight_number": "LH123",
                "Status": type(
                    "Status",
                    (),
                    {
                        "CANCELLED": "cancelled",
                        "DEPARTED": "departed",
                        "ARRIVED": "arrived",
                    },
                ),
            },
        )()

        validate_flight_status(flight)

    def test_validate_flight_status_cancelled_error(self):
        flight = type(
            "Flight",
            (),
            {
                "status": "cancelled",
                "flight_number": "LH123",
                "Status": type(
                    "Status",
                    (),
                    {
                        "CANCELLED": "cancelled",
                        "DEPARTED": "departed",
                        "ARRIVED": "arrived",
                    },
                ),
            },
        )()

        with self.assertRaises(serializers.ValidationError):
            validate_flight_status(flight)

    def test_validate_flight_status_departed_error(self):
        flight = type(
            "Flight",
            (),
            {
                "status": "departed",
                "flight_number": "LH123",
                "Status": type(
                    "Status",
                    (),
                    {
                        "CANCELLED": "cancelled",
                        "DEPARTED": "departed",
                        "ARRIVED": "arrived",
                    },
                ),
            },
        )()

        with self.assertRaises(serializers.ValidationError):
            validate_flight_status(flight)

    def test_validate_flight_status_arrived_error(self):
        flight = type(
            "Flight",
            (),
            {
                "status": "arrived",
                "flight_number": "LH123",
                "Status": type(
                    "Status",
                    (),
                    {
                        "CANCELLED": "cancelled",
                        "DEPARTED": "departed",
                        "ARRIVED": "arrived",
                    },
                ),
            },
        )()

        with self.assertRaises(serializers.ValidationError):
            validate_flight_status(flight)

    def test_validate_flight_departure_future_success(self):
        flight = type(
            "Flight",
            (),
            {
                "departure_time": timezone.now() + timedelta(days=1),
                "flight_number": "LH123",
            },
        )()

        validate_flight_departure(flight)

    def test_validate_flight_departure_past_error(self):
        flight = type(
            "Flight",
            (),
            {
                "departure_time": timezone.now() - timedelta(days=1),
                "flight_number": "LH123",
            },
        )()

        with self.assertRaises(serializers.ValidationError):
            validate_flight_departure(flight)

    def test_validate_same_flight_success(self):
        tickets = [
            {
                "flight": type("Flight", (), {"id": 1})(),
                "airplane_seat": type("Seat", (), {"id": 1})(),
            },
            {
                "flight": type("Flight", (), {"id": 1})(),
                "airplane_seat": type("Seat", (), {"id": 2})(),
            },
        ]

        validate_same_flight(tickets)

    def test_validate_same_flight_error(self):
        tickets = [
            {
                "flight": type("Flight", (), {"id": 1})(),
                "airplane_seat": type("Seat", (), {"id": 1})(),
            },
            {
                "flight": type("Flight", (), {"id": 2})(),
                "airplane_seat": type("Seat", (), {"id": 2})(),
            },
        ]

        with self.assertRaises(serializers.ValidationError):
            validate_same_flight(tickets)

    def test_validate_flight_status_delayed_success(self):
        flight = type(
            "Flight",
            (),
            {
                "status": "delayed",
                "flight_number": "LH123",
                "Status": type(
                    "Status",
                    (),
                    {
                        "CANCELLED": "cancelled",
                        "DEPARTED": "departed",
                        "ARRIVED": "arrived",
                    },
                ),
            },
        )()

        validate_flight_status(flight)

    def test_validate_flight_status_boarding_success(self):
        flight = type(
            "Flight",
            (),
            {
                "status": "boarding",
                "flight_number": "LH123",
                "Status": type(
                    "Status",
                    (),
                    {
                        "CANCELLED": "cancelled",
                        "DEPARTED": "departed",
                        "ARRIVED": "arrived",
                    },
                ),
            },
        )()

        validate_flight_status(flight)


class SeatValidatorTests(TestCase):

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
            extra_price=Decimal("0.00"),
            baggage_kg=20,
        )

        self.seat = AirplaneSeat.objects.create(
            airplane=self.airplane,
            seat_class=self.seat_class,
            row_number=1,
            seat_letter="A",
            is_active=True,
        )

        self.route = Route.objects.create(
            departure_airport=self.departure_airport,
            arrival_airport=self.arrival_airport,
            distance_km=500,
            estimated_duration=timedelta(hours=1, minutes=10),
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

    def test_validate_duplicate_seats_success(self):
        tickets = [
            {
                "flight": type("Flight", (), {"id": 1})(),
                "airplane_seat": type("Seat", (), {"id": 1})(),
            },
            {
                "flight": type("Flight", (), {"id": 1})(),
                "airplane_seat": type("Seat", (), {"id": 2})(),
            },
        ]

        validate_duplicate_seats(tickets)

    def test_validate_duplicate_seats_error(self):
        tickets = [
            {
                "flight": type("Flight", (), {"id": 1})(),
                "airplane_seat": type("Seat", (), {"id": 1})(),
            },
            {
                "flight": type("Flight", (), {"id": 1})(),
                "airplane_seat": type("Seat", (), {"id": 1})(),
            },
        ]

        with self.assertRaises(serializers.ValidationError):
            validate_duplicate_seats(tickets)

    def test_validate_seats_belong_to_flight_airplane_success(self):
        tickets = [
            {
                "flight": type(
                    "Flight",
                    (),
                    {
                        "airplane_id": 1,
                        "airplane": type("Airplane", (), {"tail_number": "UR-ABC"})(),
                    },
                )(),
                "airplane_seat": type(
                    "Seat",
                    (),
                    {
                        "airplane_id": 1,
                        "seat_number": "1A",
                    },
                )(),
            }
        ]

        validate_seats_belong_to_flight_airplane(tickets)

    def test_validate_seats_belong_to_flight_airplane_error(self):
        tickets = [
            {
                "flight": type(
                    "Flight",
                    (),
                    {
                        "airplane_id": 1,
                        "airplane": type("Airplane", (), {"tail_number": "UR-ABC"})(),
                    },
                )(),
                "airplane_seat": type(
                    "Seat",
                    (),
                    {
                        "airplane_id": 2,
                        "seat_number": "1A",
                    },
                )(),
            }
        ]

        with self.assertRaises(serializers.ValidationError):
            validate_seats_belong_to_flight_airplane(tickets)

    def test_validate_available_seats_success(self):
        tickets = [
            {
                "flight": self.flight,
                "airplane_seat": self.seat,
            }
        ]

        validate_available_seats(tickets)

    def test_validate_available_seats_pending_error(self):
        booking = Booking.objects.create(
            user=self.user,
            status=Booking.Status.PENDING,
            total_price=Decimal("100.00"),
        )

        Ticket.objects.create(
            booking=booking,
            flight=self.flight,
            airplane_seat=self.seat,
            passenger_first_name="John",
            passenger_last_name="Doe",
            price=Decimal("100.00"),
            status=Ticket.Status.PENDING,
        )

        tickets = [
            {
                "flight": self.flight,
                "airplane_seat": self.seat,
            }
        ]

        with self.assertRaises(serializers.ValidationError):
            validate_available_seats(tickets)

    def test_validate_available_seats_paid_error(self):
        booking = Booking.objects.create(
            user=self.user,
            status=Booking.Status.PAID,
            total_price=Decimal("100.00"),
        )

        Ticket.objects.create(
            booking=booking,
            flight=self.flight,
            airplane_seat=self.seat,
            passenger_first_name="John",
            passenger_last_name="Doe",
            price=Decimal("100.00"),
            status=Ticket.Status.PAID,
        )

        tickets = [
            {
                "flight": self.flight,
                "airplane_seat": self.seat,
            }
        ]

        with self.assertRaises(serializers.ValidationError):
            validate_available_seats(tickets)

    def test_validate_available_seats_cancelled_success(self):
        booking = Booking.objects.create(
            user=self.user,
            status=Booking.Status.CANCELLED,
            total_price=Decimal("100.00"),
        )

        Ticket.objects.create(
            booking=booking,
            flight=self.flight,
            airplane_seat=self.seat,
            passenger_first_name="John",
            passenger_last_name="Doe",
            price=Decimal("100.00"),
            status=Ticket.Status.CANCELLED,
        )

        tickets = [
            {
                "flight": self.flight,
                "airplane_seat": self.seat,
            }
        ]

        validate_available_seats(tickets)
