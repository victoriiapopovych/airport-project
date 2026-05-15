from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from .models import TicketClass, Booking, Ticket
from .serializers import TicketClassSerializer, BookingListSerializer, BookingDetailSerializer, TicketListSerializer, TicketDetailSerializer


class TicketClassListCreateAPIView(APIView):
    serializer_class = TicketClassSerializer

    def get(self, request):
        ticket_classes = TicketClass.objects.all()
        serializer = TicketClassSerializer(ticket_classes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TicketClassSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TicketClassDetailAPIView(APIView):
    serializer_class = TicketClassSerializer

    def get_object(self, pk):
        return get_object_or_404(TicketClass, pk=pk)

    def get(self, request, pk):
        ticket_class = self.get_object(pk)
        serializer = TicketClassSerializer(ticket_class)
        return Response(serializer.data)

    def put(self, request, pk):
        ticket_class = self.get_object(pk)
        serializer = TicketClassSerializer(ticket_class, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        ticket_class = self.get_object(pk)
        serializer = TicketClassSerializer(ticket_class, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        ticket_class = self.get_object(pk)
        ticket_class.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    def get_serializer_class(self):
        if self.action == "list":
            return BookingListSerializer
        
        if self.action == "retrieve":
            return BookingDetailSerializer

        return BookingDetailSerializer


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    
    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer
        
        if self.action == "retrieve":
            return TicketDetailSerializer
        
        return TicketDetailSerializer
