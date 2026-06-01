from rest_framework import viewsets, generics
from .models import Airline, AirplaneType, Airplane, SeatClass, AirplaneSeat
from .serializers import AirlineListSerializer, AirlineDetailSerializer, AirplaneTypeSerializer, AirplaneListSerializer, AirplaneDetailSerializer, SeatClassSerializer, AirplaneSeatListSerializer, AirplaneSeatDetailSerializer

from config.permissions import IsManagerOrAdminOrReadOnly

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from .filters import AirlineFilter, AirplaneTypeFilter, AirplaneFilter

from config.pagination import CustomPagination


class AirlineViewSet(viewsets.ModelViewSet):
    queryset = Airline.objects.all()
    permission_classes = [IsManagerOrAdminOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = AirlineFilter
    search_fields = ["name", "iata_code"]

    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == "list":
            return AirlineListSerializer

        return AirlineDetailSerializer


class AirplaneTypeListCreateAPIView(generics.ListCreateAPIView):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = [IsManagerOrAdminOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = AirplaneTypeFilter
    search_fields = ["manufacturer", "code"]

    pagination_class = CustomPagination

class AirplaneTypeRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = [IsManagerOrAdminOrReadOnly]


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    permission_classes = [IsManagerOrAdminOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = AirplaneFilter
    search_fields = ["tail_number", "airline__name", "airplane_type__code"]

    pagination_class = CustomPagination
    
    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        
        return AirplaneDetailSerializer
    

class SeatClassViewSet(viewsets.ModelViewSet):
    queryset = SeatClass.objects.all()
    serializer_class = SeatClassSerializer
    permission_classes = [IsManagerOrAdminOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["airline", "class_type", "priority_boarding", "lounge_access"]
    search_fields = ["airline__name", "class_type"]

    pagination_class = CustomPagination

class AirplaneSeatViewSet(viewsets.ModelViewSet):
    queryset = AirplaneSeat.objects.all()
    permission_classes = [IsManagerOrAdminOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["airplane", "seat_class", "is_window", "is_aisle", "is_exit_row", "has_extra_legroom", "is_active"]
    search_fields = ["airplane__tail_number", "seat_letter", "seat_class__class_type"]

    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneSeatListSerializer

        return AirplaneSeatDetailSerializer

