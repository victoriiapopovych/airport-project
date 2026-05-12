from rest_framework import viewsets
from .models import TicketClass, Booking, Ticket
from .serializers import TicketClassSerializer, BookingSerializer, TicketSerializer


class TicketClassViewSet(viewsets.ModelViewSet):
    queryset = TicketClass.objects.all()
    serializer_class = TicketClassSerializer


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
