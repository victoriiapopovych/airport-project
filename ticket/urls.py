from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TicketClassViewSet, BookingViewSet, TicketViewSet


router = DefaultRouter()

router.register("ticket-classes", TicketClassViewSet)
router.register("bookings", BookingViewSet)
router.register("tickets", TicketViewSet)


urlpatterns = [
    path("", include(router.urls)),
]
