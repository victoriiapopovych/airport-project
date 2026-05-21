from rest_framework import viewsets, generics
from .models import Country, City, Airport
from .serializers import CountrySerializer, CitySerializer, AirportDetailSerializer, AirportListSerializer

from config.permissions import IsAdminOrReadOnly
from user.permissions import IsManagerOrAdminOrReadOnly

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from config.pagination import CustomPagination

class CountryListCreateAPIView(generics.ListCreateAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [IsAdminOrReadOnly]

    pagination_class = CustomPagination


class CountryRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [IsAdminOrReadOnly]


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [IsAdminOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["country"]
    search_fields = ["name"]

    pagination_class = CustomPagination


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    permission_classes = [IsManagerOrAdminOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["city"]
    search_fields = ["code", "name"]

    pagination_class = CustomPagination
    
    def get_serializer_class(self):
        if self.action == "list":
            return AirportListSerializer
        
        return AirportDetailSerializer
