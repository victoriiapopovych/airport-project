from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from user.models import User
from location.models import Country, City, Airport
from airline.models import Airline, AirplaneType, Airplane, SeatClass, AirplaneSeat
from flight.models import Route, Flight
from flight.services import calculate_ticket_price, get_taken_seat_ids_for_flight, get_available_seats_for_flight, get_available_seats_count_for_flight
from ticket.models import Booking, Ticket


class FlightServiceTests(TestCase):

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

        self.seat_1 = AirplaneSeat.objects.create(
            airplane=self.airplane,
            seat_class=self.seat_class,
            row_number=1,
            seat_letter="A",
            is_active=True,
        )

        self.seat_2 = AirplaneSeat.objects.create(
            airplane=self.airplane,
            seat_class=self.seat_class,
            row_number=1,
            seat_letter="B",
            is_active=True,
        )

        self.inactive_seat = AirplaneSeat.objects.create(
            airplane=self.airplane,
            seat_class=self.seat_class,
            row_number=1,
            seat_letter="C",
            is_active=False,
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
            self.seat_1,
        )

        self.assertEqual(
            price,
            Decimal("150.00"),
        )

    def test_get_taken_seat_ids_for_flight_pending_ticket(self):
        booking = Booking.objects.create(
            user=self.user,
            status=Booking.Status.PENDING,
            total_price=Decimal("150.00"),
        )

        Ticket.objects.create(
            booking=booking,
            flight=self.flight,
            airplane_seat=self.seat_1,
            passenger_first_name="John",
            passenger_last_name="Doe",
            price=Decimal("150.00"),
            status=Ticket.Status.PENDING,
        )

        taken_seat_ids = list(
            get_taken_seat_ids_for_flight(self.flight)
        )

        self.assertIn(
            self.seat_1.id,
            taken_seat_ids,
        )

    def test_get_taken_seat_ids_for_flight_paid_ticket(self):
        booking = Booking.objects.create(
            user=self.user,
            status=Booking.Status.PAID,
            total_price=Decimal("150.00"),
        )

        Ticket.objects.create(
            booking=booking,
            flight=self.flight,
            airplane_seat=self.seat_1,
            passenger_first_name="John",
            passenger_last_name="Doe",
            price=Decimal("150.00"),
            status=Ticket.Status.PAID,
        )

        taken_seat_ids = list(
            get_taken_seat_ids_for_flight(self.flight)
        )

        self.assertIn(
            self.seat_1.id,
            taken_seat_ids,
        )

    def test_get_taken_seat_ids_for_flight_cancelled_ticket_not_included(self):
        booking = Booking.objects.create(
            user=self.user,
            status=Booking.Status.CANCELLED,
            total_price=Decimal("150.00"),
        )

        Ticket.objects.create(
            booking=booking,
            flight=self.flight,
            airplane_seat=self.seat_1,
            passenger_first_name="John",
            passenger_last_name="Doe",
            price=Decimal("150.00"),
            status=Ticket.Status.CANCELLED,
        )

        taken_seat_ids = list(
            get_taken_seat_ids_for_flight(self.flight)
        )

        self.assertNotIn(
            self.seat_1.id,
            taken_seat_ids,
        )

    def test_get_available_seats_for_flight_returns_only_available_seats(self):
        booking = Booking.objects.create(
            user=self.user,
            status=Booking.Status.PENDING,
            total_price=Decimal("150.00"),
        )

        Ticket.objects.create(
            booking=booking,
            flight=self.flight,
            airplane_seat=self.seat_1,
            passenger_first_name="John",
            passenger_last_name="Doe",
            price=Decimal("150.00"),
            status=Ticket.Status.PENDING,
        )

        available_seats = list(
            get_available_seats_for_flight(self.flight)
        )

        self.assertIn(
            self.seat_2,
            available_seats,
        )

        self.assertNotIn(
            self.seat_1,
            available_seats,
        )

        self.assertNotIn(
            self.inactive_seat,
            available_seats,
        )

    def test_get_available_seats_count_for_flight(self):
        booking = Booking.objects.create(
            user=self.user,
            status=Booking.Status.PENDING,
            total_price=Decimal("150.00"),
        )

        Ticket.objects.create(
            booking=booking,
            flight=self.flight,
            airplane_seat=self.seat_1,
            passenger_first_name="John",
            passenger_last_name="Doe",
            price=Decimal("150.00"),
            status=Ticket.Status.PENDING,
        )

        available_seats_count = get_available_seats_count_for_flight(
            self.flight
        )

        self.assertEqual(
            available_seats_count,
            1,
        )