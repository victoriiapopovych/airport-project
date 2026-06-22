from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from location.models import Country, City, Airport
from airline.models import Airline, AirplaneType, Airplane, SeatClass, AirplaneSeat
from flight.models import Route, Flight
from flight.serializers import FlightDetailSerializer, AvailableSeatSerializer


class FlightSerializerTests(TestCase):

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

        self.other_airline = Airline.objects.create(
            name="Ryanair",
            iata_code="FR",
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

        self.empty_airplane = Airplane.objects.create(
            tail_number="D-EMPTY",
            airline=self.airline,
            airplane_type=self.airplane_type,
            manufactured_year=2021,
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

        self.route = Route.objects.create(
            departure_airport=self.departure_airport,
            arrival_airport=self.arrival_airport,
            distance_km=500,
            estimated_duration=timedelta(hours=1),
        )

    def test_flight_serializer_valid_data(self):
        data = {
            "flight_number": "LH123",
            "route": self.route.id,
            "airline": self.airline.id,
            "airplane": self.airplane.id,
            "departure_time": timezone.now() + timedelta(days=1),
            "arrival_time": timezone.now() + timedelta(days=1, hours=2),
            "status": Flight.Status.SCHEDULED,
            "terminal_name": "A",
            "boarding_gate": "B12",
            "base_price": Decimal("100.00"),
        }

        serializer = FlightDetailSerializer(data=data)

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_flight_serializer_airplane_belongs_to_airline_error(self):
        data = {
            "flight_number": "LH123",
            "route": self.route.id,
            "airline": self.other_airline.id,
            "airplane": self.airplane.id,
            "departure_time": timezone.now() + timedelta(days=1),
            "arrival_time": timezone.now() + timedelta(days=1, hours=2),
            "status": Flight.Status.SCHEDULED,
            "terminal_name": "A",
            "boarding_gate": "B12",
            "base_price": Decimal("100.00"),
        }

        serializer = FlightDetailSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("airplane", serializer.errors)

    def test_flight_serializer_airplane_without_seats_error(self):
        data = {
            "flight_number": "LH123",
            "route": self.route.id,
            "airline": self.airline.id,
            "airplane": self.empty_airplane.id,
            "departure_time": timezone.now() + timedelta(days=1),
            "arrival_time": timezone.now() + timedelta(days=1, hours=2),
            "status": Flight.Status.SCHEDULED,
            "terminal_name": "A",
            "boarding_gate": "B12",
            "base_price": Decimal("100.00"),
        }

        serializer = FlightDetailSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("airplane", serializer.errors)

    def test_flight_serializer_arrival_before_departure_error(self):
        data = {
            "flight_number": "LH123",
            "route": self.route.id,
            "airline": self.airline.id,
            "airplane": self.airplane.id,
            "departure_time": timezone.now() + timedelta(days=1),
            "arrival_time": timezone.now() + timedelta(hours=12),
            "status": Flight.Status.SCHEDULED,
            "terminal_name": "A",
            "boarding_gate": "B12",
            "base_price": Decimal("100.00"),
        }

        serializer = FlightDetailSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("arrival_time", serializer.errors)

    def test_available_seat_serializer_ticket_price(self):
        serializer = AvailableSeatSerializer(
            instance=self.seat,
            context={"flight": type("Flight", (), {"base_price": Decimal("100.00")})()},
        )

        data = serializer.data

        self.assertEqual(
            data["ticket_price"],
            Decimal("150.00"),
        )