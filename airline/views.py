from rest_framework import viewsets, generics
from .models import Airline, AirplaneType, Airplane
from .serializers import AirlineListSerializer, AirlineDetailSerializer, AirplaneTypeSerializer, AirplaneListSerializer, AirplaneDetailSerializer


class AirlineViewSet(viewsets.ModelViewSet):
    queryset = Airline.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return AirlineListSerializer

        if self.action == "retrieve":
            return AirlineDetailSerializer
        
        return AirlineDetailSerializer


class AirplaneTypeRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class AirplaneTypeListCreateAPIView(generics.ListCreateAPIView):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    
    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
    
        if self.action == "retrieve":
            return AirplaneDetailSerializer
        
        return AirplaneDetailSerializer

