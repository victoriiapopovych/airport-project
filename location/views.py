from rest_framework import viewsets, generics
from .models import Country, City, Airport
from .serializers import CountrySerializer, CitySerializer, AirportDetailSerializer, AirportListSerializer


class CountryListCreateAPIView(generics.ListCreateAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


class CountryRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    
    def get_serializer_class(self):
        if self.action == "list":
            return AirportListSerializer
        
        if self.action == "retrieve":
            return AirportDetailSerializer
        
        return AirportDetailSerializer
