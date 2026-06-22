from django.test import TestCase
from django.contrib.auth.models import AnonymousUser
from rest_framework.test import APIRequestFactory

from user.models import User
from ticket.permissions import CanViewAllBookings, CanCreateBooking, CanCancelBooking


class CanViewAllBookingsTests(TestCase):

    def test_support_can_view_all_bookings(self):
        user = User(
            email="support@test.com",
            role=User.Role.SUPPORT,
        )

        request = APIRequestFactory().get("/")
        request.user = user

        permission = CanViewAllBookings()

        self.assertTrue(
            permission.has_permission(
                request,
                None,
            )
        )

    def test_manager_can_view_all_bookings(self):
        user = User(
            email="manager@test.com",
            role=User.Role.MANAGER,
        )

        request = APIRequestFactory().get("/")
        request.user = user

        permission = CanViewAllBookings()

        self.assertTrue(
            permission.has_permission(request, None)
        )


    def test_staff_can_view_all_bookings(self):
        user = User(
            email="staff@test.com",
            is_staff=True,
        )

        request = APIRequestFactory().get("/")
        request.user = user

        permission = CanViewAllBookings()

        self.assertTrue(
            permission.has_permission(request, None)
        )


    def test_passenger_cannot_view_all_bookings(self):
        user = User(
            email="passenger@test.com",
            role=User.Role.PASSENGER,
        )

        request = APIRequestFactory().get("/")
        request.user = user

        permission = CanViewAllBookings()

        self.assertFalse(
            permission.has_permission(request, None)
        )


    def test_anonymous_cannot_view_all_bookings(self):
        request = APIRequestFactory().get("/")
        request.user = AnonymousUser()

        permission = CanViewAllBookings()

        self.assertFalse(
            permission.has_permission(request, None)
        )


class CanCreateBookingTests(TestCase):

    def test_verified_passenger_can_create_booking(self):
        user = User(
            email="passenger@test.com",
            role=User.Role.PASSENGER,
            is_verified=True,
        )

        request = APIRequestFactory().post("/")
        request.user = user

        permission = CanCreateBooking()

        self.assertTrue(
            permission.has_permission(request, None)
        )


    def test_unverified_passenger_cannot_create_booking(self):
        user = User(
            email="passenger@test.com",
            role=User.Role.PASSENGER,
            is_verified=False,
        )

        request = APIRequestFactory().post("/")
        request.user = user

        permission = CanCreateBooking()

        self.assertFalse(
            permission.has_permission(request, None)
        )


    def test_support_cannot_create_booking(self):
        user = User(
            email="support@test.com",
            role=User.Role.SUPPORT,
            is_verified=True,
        )

        request = APIRequestFactory().post("/")
        request.user = user

        permission = CanCreateBooking()

        self.assertFalse(
            permission.has_permission(request, None)
        )


    def test_manager_cannot_create_booking(self):
        user = User(
            email="manager@test.com",
            role=User.Role.MANAGER,
            is_verified=True,
        )

        request = APIRequestFactory().post("/")
        request.user = user

        permission = CanCreateBooking()

        self.assertFalse(
            permission.has_permission(request, None)
        )


class CanCancelBookingTests(TestCase):

    def test_owner_can_cancel_booking(self):
        user = User(
            email="user@test.com",
            role=User.Role.PASSENGER,
            is_verified=True,
        )

        booking = type("Booking", (), {"user": user})()

        request = APIRequestFactory().post("/")
        request.user = user

        permission = CanCancelBooking()

        self.assertTrue(
            permission.has_object_permission(
                request,
                None,
                booking,
            )
        )


    def test_other_user_cannot_cancel_booking(self):
        owner = User(
            email="owner@test.com",
            role=User.Role.PASSENGER,
            is_verified=True,
        )

        other_user = User(
            email="other@test.com",
            role=User.Role.PASSENGER,
            is_verified=True,
        )

        booking = type("Booking", (), {"user": owner})()

        request = APIRequestFactory().post("/")
        request.user = other_user

        permission = CanCancelBooking()

        self.assertFalse(
            permission.has_object_permission(
                request,
                None,
                booking,
            )
        )

    def test_manager_can_cancel_any_booking(self):
        manager = User(
            email="manager@test.com",
            role=User.Role.MANAGER,
        )

        owner = User(
            email="owner@test.com",
            role=User.Role.PASSENGER,
        )

        booking = type("Booking", (), {"user": owner})()

        request = APIRequestFactory().post("/")
        request.user = manager

        permission = CanCancelBooking()

        self.assertTrue(
            permission.has_object_permission(
                request,
                None,
                booking,
            )
        )


    def test_anonymous_cannot_cancel_booking(self):
        owner = User(
            email="owner@test.com",
            role=User.Role.PASSENGER,
        )

        booking = type("Booking", (), {"user": owner})()

        request = APIRequestFactory().post("/")
        request.user = AnonymousUser()

        permission = CanCancelBooking()

        self.assertFalse(
            permission.has_object_permission(
                request,
                None,
                booking,
            )
        )