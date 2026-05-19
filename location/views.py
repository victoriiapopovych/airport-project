from rest_framework import viewsets, generics
from .models import Country, City, Airport
from .serializers import CountrySerializer, CitySerializer, AirportDetailSerializer, AirportListSerializer

from config.permissions import IsAdminOrReadOnly
from user.permissions import IsManagerOrAdminOrReadOnly


class CountryListCreateAPIView(generics.ListCreateAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [IsAdminOrReadOnly]


class CountryRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [IsAdminOrReadOnly]


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [IsAdminOrReadOnly]


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    permission_classes = [IsManagerOrAdminOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == "list":
            return AirportListSerializer
        
        if self.action == "retrieve":
            return AirportDetailSerializer
        
        return AirportDetailSerializer
