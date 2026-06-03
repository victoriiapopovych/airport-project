from rest_framework import viewsets, generics, mixins
from .models import Airline, AirplaneType, Airplane, SeatClass, AirplaneSeat
from .serializers import AirlineListSerializer, AirlineDetailSerializer, AirplaneTypeSerializer, AirplaneListSerializer, AirplaneDetailSerializer, SeatClassSerializer, AirplaneSeatListSerializer, AirplaneSeatDetailSerializer, AirplaneSeatGenerationSerializer

from config.permissions import IsManagerOrAdminOrReadOnly

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from .filters import AirlineFilter, AirplaneTypeFilter, AirplaneFilter

from config.pagination import CustomPagination

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from .services import generate_airplane_seats

import logging
logger = logging.getLogger(__name__)


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
        
        if self.action == "generate_seats":
            return AirplaneSeatGenerationSerializer
        
        return AirplaneDetailSerializer
    
    @action(detail=True, methods=["post"], url_path="generate-seats", serializer_class=AirplaneSeatGenerationSerializer)
    def generate_seats(self, request, pk=None):
        airplane = self.get_object()

        logger.info(
            "User %s started seat generation for airplane %s.",
            self.request.user.id if self.request.user.is_authenticated else "anonymous",
            airplane.tail_number,
        )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        try:
            created_count = generate_airplane_seats(
                airplane=airplane,
                rows=data.get("rows", 30),
                letters=data.get("letters", ["A", "B", "C", "D", "E", "F"]),
                class_rows=data.get("class_rows", {}),
                exit_rows=data.get("exit_rows", []),
                window_letters=data.get("window_letters", None),
                aisle_letters=data.get("aisle_letters", []),
            )

        except ValueError as error:
            logger.warning(
                "Seat generation failed for airplane %s by user %s: %s",
                airplane.tail_number,
                self.request.user.id if self.request.user.is_authenticated else "anonymous",
                str(error),
            )

            return Response(
                {"detail": str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )

        logger.info(
            "User %s successfully generated %s seats for airplane %s.",
            self.request.user.id if self.request.user.is_authenticated else "anonymous",
            created_count,
            airplane.tail_number,
        )

        return Response(
            {"detail": f"{created_count} seats were generated successfully."},
            status=status.HTTP_201_CREATED
        )
    

class SeatClassViewSet(viewsets.ModelViewSet):
    queryset = SeatClass.objects.all()
    serializer_class = SeatClassSerializer
    permission_classes = [IsManagerOrAdminOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["airline", "class_type", "priority_boarding", "lounge_access"]
    search_fields = ["airline__name", "class_type"]

    pagination_class = CustomPagination

class AirplaneSeatViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
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

