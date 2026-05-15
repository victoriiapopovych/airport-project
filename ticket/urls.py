from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TicketClassListCreateAPIView, TicketClassDetailAPIView, BookingViewSet, TicketViewSet


router = DefaultRouter()

router.register("bookings", BookingViewSet)
router.register("tickets", TicketViewSet)


urlpatterns = [
    path("", include(router.urls)),

    path(
    "ticket-classes/",
    TicketClassListCreateAPIView.as_view(),
    name="ticket-class-list-create",
    ),
    path(
        "ticket-classes/<int:pk>/",
        TicketClassDetailAPIView.as_view(),
        name="ticket-class-detail",
    ),
]
