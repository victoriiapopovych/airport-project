from rest_framework import viewsets, generics
from .models import Airline, AirplaneType, Airplane
from .serializers import AirlineListSerializer, AirlineDetailSerializer, AirplaneTypeSerializer, AirplaneListSerializer, AirplaneDetailSerializer

from user.permissions import IsManagerOrAdminOrReadOnly

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

